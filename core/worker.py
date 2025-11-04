import time
import random
from instagrapi import Client
import requests
from instagrapi.exceptions import LoginRequired, ChallengeRequired, TwoFactorRequired
from utils.logger import log_message
from utils.telegram import telegram_monitor
from .auth import handle_login

USER_AGENTS = [
    "Instagram 289.0.0.77.109 Android (33/13; 420dpi; 1080x2400; samsung; SM-G998B; crownlte; qcom; en_US)",
    "Instagram 301.0.0.81.110 Android (34/14; 440dpi; 1080x2408; google; Pixel 7; panther; qcom; en_US)",
    "Instagram 295.0.0.32.110 Android (33/13; 480dpi; 1080x2400; OnePlus; ONEPLUS A6013; OnePlus6T; qcom; en_GB)",
]

def _perform_login_with_retries(cl: Client, config: dict) -> bool:
    """
    Attempts to log in up to 3 times with a delay between failures.
    """
    login_attempts = 0
    while login_attempts < 3:
        try:
            if handle_login(cl, config):
                return True
           
        except (ChallengeRequired, TwoFactorRequired) as e:
            log_message("Instagram requires a verification code to continue.")
            try:
                
                print("\n[!] A 6-digit code may have been sent to your registered Email or SMS.")
                print("    If you only see a 'This was me' prompt, approve it and press Enter here without typing a code.")
                code = input("Enter the 6-digit code (or leave blank to retry after approval): ").strip()
                
                if not code:
                    log_message("No code entered. Waiting 60 seconds for you to approve the login manually...")
                    time.sleep(60)
                    continue 
                
                log_message("Verifying code with Instagram...")
                cl.challenge_code_verify(code)
                
                log_message("Verification successful! Login complete.")
                cl.dump_settings(config.get('ENV_FILE_PATH').with_suffix('.session.json'))
                return True 
            except Exception as e:
                log_message(f"Challenge verification failed: {e}. Retrying login process...")
        
        login_attempts += 1
        log_message(f"Login failed. Retrying in 60 seconds... (Attempt {login_attempts} of 3)")
        time.sleep(60)
    
    log_message("Login failed after 3 attempts. Stopping bot.")
    
    telegram_token = config.get('TELEGRAM_TOKEN')
    telegram_chat_id = config.get('TELEGRAM_CHAT')
    error_message = (
        "🚨 *CRITICAL: LOGIN FAILED* 🚨\n\n"
        "The bot failed to log in after 3 attempts and has stopped. Please check your credentials, session, or potential Instagram blocks and restart the bot manually."
    )
    telegram_monitor.send_message(telegram_token, telegram_chat_id, error_message)
    return False

def run_worker(config: dict, task_function):
    """
    Manages the main bot loop, including login, re-login, and interval waits.
    Executes a given task function in each cycle.
    """
    cl = Client()
    cl.private_requests = True

    cl.user_agent = random.choice(USER_AGENTS)
    log_message(f"Using User-Agent: ...{cl.user_agent[-50:]}")

    proxy = config.get('PROXY')
    if proxy:
        cl.set_proxy(proxy)
        log_message(f"Using proxy: {proxy}")

    cl.delay_range = [8, 16]

    if not _perform_login_with_retries(cl, config):
        return

    telegram_token = config.get('TELEGRAM_TOKEN')
    telegram_chat_id = config.get('TELEGRAM_CHAT')

    while True:
        try:
            from .lover import lover_task
            from .follower_viewer import follower_viewer_task

            current_config = config.copy()
            if task_function in [lover_task, follower_viewer_task] and 'TARGETS' in current_config and current_config['TARGETS']:
                selected_target = random.choice(current_config['TARGETS'])
                current_config['TARGET'] = selected_target
                log_message(f"🎯 Selected target for this cycle: @{selected_target}")

            cl.get_timeline_feed()
            actions_count = task_function(cl, current_config) or 0

            if actions_count > 0:
                interval = random.randint(config['MIN_INTERVAL'], config['MAX_INTERVAL'])
                log_message(f"Task complete ({actions_count} actions). Waiting for {interval}s (normal).")
            else:
                interval = config['SHORT_INTERVAL']
                log_message(f"Task complete (0 actions). Waiting for {interval}s (short).")

            wait_end = time.time() + interval
            telegram_monitor.next_run_times['main'] = time.strftime("%H:%M:%S", time.localtime(wait_end))
            log_message(f"Task complete. Waiting for {interval} seconds until next cycle.")
            time.sleep(interval)
        except LoginRequired as e:
            log_message(f"Session dead or expired: {e}. Attempting to re-login...")
            if not _perform_login_with_retries(cl, config):
                break
        except requests.exceptions.ConnectionError as e:
            log_message(f"Connection issue: {e}. Retrying in 5 minutes.")
            time.sleep(300)
        except KeyboardInterrupt:
            log_message("Bot stopped by user (Ctrl+C).")
            break
        except Exception as e:
            error_str = str(e)
            if error_str.strip().startswith(('<!DOCTYPE html>', '<script>')):
                log_message("Error in worker loop: Received an unexpected HTML response from Instagram. This may indicate a session issue or a block. Retrying in 60s.")
            else:
                log_message(f"Error in worker loop: {e}")
            time.sleep(60)
