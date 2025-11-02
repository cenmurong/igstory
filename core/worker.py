import time
import random
from instagrapi import Client
import requests
from instagrapi.exceptions import LoginRequired
from utils.logger import log_message
from utils.telegram import telegram_monitor
from .auth import handle_login

USER_AGENTS = [
    "Instagram 153.0.0.34.96 Android (28/9; 420dpi; 1080x2220; samsung; SM-G960F; starlte; samsungexynos9810; en_US)", # Samsung S9
    "Instagram 113.0.0.39.122 Android (24/7.0; 420dpi; 1080x1920; samsung; SM-G950F; dreamlte; samsungexynos8895; en_US)", # Samsung S8
    "Instagram 76.0.0.15.395 Android (24/7.0; 640dpi; 1440x2560; samsung; SM-G930F; herolte; samsungexynos8890; en_US)", # Samsung S7
]

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

    login_attempts = 0
    while login_attempts < 3:
        if handle_login(cl, config):
            break  
        login_attempts += 1
        if login_attempts < 3:
            log_message(f"Initial login failed. Retrying in 60 seconds... (Attempt {login_attempts}/3)")
            time.sleep(60)
    else:
        log_message("Initial login failed after 3 attempts. Stopping bot.")
        return

    while True:
        try:
            cl.get_timeline_feed()
            task_function(cl, config)

            wait_end = time.time() + config['INTERVAL']
            telegram_monitor.next_run_time = time.strftime("%H:%M:%S", time.localtime(wait_end))
            while time.time() < wait_end:
                telegram_monitor.check_commands(config['TELEGRAM_TOKEN'], config['TELEGRAM_CHAT'])
                telegram_monitor.send_health_ping(config['TELEGRAM_TOKEN'], config['TELEGRAM_CHAT'])
                time.sleep(5)
        except LoginRequired as e:
            log_message(f"Session dead or expired: {e}. Attempting to re-login...")
            config['SESSION_ID'] = None
            if not handle_login(cl, config):
                log_message("Re-login failed, bot stopping.")
                break
        except requests.exceptions.ConnectionError as e:
            log_message(f"Connection issue: {e}. Retrying in 5 minutes.")
            time.sleep(300)
        except Exception as e:
            log_message(f"Error in worker loop: {e}")
            time.sleep(60)
