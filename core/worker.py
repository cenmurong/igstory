import time
import random
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
from utils.logger import log_message
from utils.telegram import telegram_monitor
from .auth import handle_login

USER_AGENTS = [
    "Instagram 27.0.0.7.97 Android (24/7.0; 380dpi; 1080x1920; OnePlus; ONEPLUS A3003; OnePlus3T; qcom; en_US)",
    "Instagram 10.26.0 Android (24/7.0; 480dpi; 1080x1920; LGE/lge; LG-H870; lucye; qcom; en_US)",
    "Instagram 10.34.0 Android (24/7.0; 480dpi; 1080x1920; samsung; SM-G955F; dream2lte; samsungexynos8895; en_US)",
]

def run_worker(config: dict, task_function):

    cl = Client()
    cl.private_requests = True

    cl.user_agent = random.choice(USER_AGENTS)
    log_message(f"Using User-Agent: ...{cl.user_agent[-50:]}")

    proxy = config.get('PROXY')
    if proxy:
        cl.set_proxy(proxy)
        log_message(f"Using proxy: {proxy}")

    cl.delay_range = [8, 16]

    if not handle_login(cl, config):
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
