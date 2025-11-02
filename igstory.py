import json
import time
import random
import requests
import logging
from pathlib import Path
from collections import deque
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ClientError
from dotenv import load_dotenv
import os
import getpass


logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s WIB] %(message)s',
    datefmt='%d %b %Y, %H:%M:%S',
    handlers=[
        logging.FileHandler("bot.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
log_message = logging.info


BANNER = r"""
   _         _____  ___         _____  __  __    __   __  _____  ___  __      
  /_\  /\ /\/__   \/___\ /\   /\\_   \/__\/ / /\ \ \ / _\/__   \/___\/__\/\_/\
 //_\\/ / \ \ / /\//  // \ \ / / / /\/_\  \ \/  \/ / \ \   / /\//  // \//\_ _/
/  _  \ \_/ // / / \_//   \ V /\/ /_//__   \  /\  /  _\ \ / / / \_// _  \ / \ 
\_/ \_/\___/ \/  \___/     \_/\____/\__/    \/  \/   \__/ \/  \___/\/ \_/ \_/ 
                                                                              
"""


Story = None
try:
    from instagrapi.models import Story  
    log_message("instagrapi v2+ detected")
except ImportError:
    try:
        from instagrapi.types import Story  
        log_message("instagrapi v1.x detected")
    except ImportError:
        log_message("instagrapi not detected! Install: pip install instagrapi")
        exit()



def patch_scans_profile():
    if Story is None:
        log_message("Story model not found → skip patch")
        return
    try:
        original_validate = Story.model_validate

        def safe_validate(cls, data):
            if isinstance(data, dict):
                for cand in data.get('image_versions2', {}).get('candidates', []):
                    if cand.get('scans_profile') is None:
                        cand['scans_profile'] = ""
            return original_validate(cls, data)
        Story.model_validate = classmethod(safe_validate)
        log_message("FIX: scans_profile=None → '' (APPLIED)")
    except Exception as e:
        log_message(f"Patch failed (safe): {e}")



patch_scans_profile()



def interactive_setup():
    print("\n\033[93m=== AUTO STORY VIEWER V.1 ===\033[0m")
    config = {}
    print("\n1. Instagram Username:")
    config['INSTAGRAM_USERNAME'] = input("   → ").strip()
    print("\n2. Instagram Password:")
    config['INSTAGRAM_PASSWORD'] = getpass.getpass("   → ")
    print("\n3. Telegram Bot Token (leave empty if not used):")
    config['TELEGRAM_BOT_TOKEN'] = input("   → ").strip()
    print("\n4. Telegram Chat ID (leave empty if not used):")
    config['TELEGRAM_CHAT_ID'] = input("   → ").strip()
    print("\n5. Interval (seconds, default 600):")
    config['CHECK_INTERVAL'] = input("   → ").strip() or "600"
    print("\n6. Max Following (default 100):")
    config['MAX_FOLLOWING'] = input("   → ").strip() or "100"
    print("\n7. Proxy (http://user:pass@ip:port, leave empty if not used):")
    config['PROXY'] = input("   → ").strip()
    config['SESSION_FILE'] = "ig_session.json"
    config['VIEW_DELAY'] = "4"

    env_path = Path(".env")
    env_path.write_text("\n".join([f"{k}={v}" for k, v in config.items()]))
    print(f"\n\033[92mSetup complete! .env file created.\033[0m")
    log_message("Interactive setup finished.")
    return config


def load_config():
    env_path = Path(".env")
    if not env_path.exists():
        log_message(".env not found → showing setup menu")
        print(BANNER)
        return interactive_setup()
    load_dotenv()
    config = {
        'INSTAGRAM_USERNAME': os.getenv('INSTAGRAM_USERNAME'),
        'INSTAGRAM_PASSWORD': os.getenv('INSTAGRAM_PASSWORD'),
        'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN'),
        'TELEGRAM_CHAT_ID': os.getenv('TELEGRAM_CHAT_ID'),
        'CHECK_INTERVAL': os.getenv('CHECK_INTERVAL', '600'),
        'MAX_FOLLOWING': os.getenv('MAX_FOLLOWING', '100'),
        'PROXY': os.getenv('PROXY'),
        'SESSION_FILE': os.getenv('SESSION_FILE', 'ig_session.json'),
    }
    if not config['INSTAGRAM_USERNAME'] or not config['INSTAGRAM_PASSWORD']:
        log_message("Login details incomplete! Delete .env and run again.")
        env_path.unlink(missing_ok=True)
        return interactive_setup()
    return config


config = load_config()
USERNAME = config['INSTAGRAM_USERNAME']
PASSWORD = config['INSTAGRAM_PASSWORD']
SESSION_FILE = Path(config['SESSION_FILE'])
CHECK_INTERVAL = int(config['CHECK_INTERVAL'])
MAX_FOLLOWING = int(config['MAX_FOLLOWING'])
TELEGRAM_BOT_TOKEN = config['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = config['TELEGRAM_CHAT_ID']
PROXY = config['PROXY']

SEEN_FILE = Path("seen_stories.json")


def load_seen_stories():
    if SEEN_FILE.exists():
        try:
            with open(SEEN_FILE, 'r') as f:
                data = json.load(f)
                now = time.time()
                data = {pk: ts for pk, ts in data.items() if now - ts < 86400}
                save_seen_stories(data)
                return data
        except:
            pass
    return {}


def save_seen_stories(data):
    with open(SEEN_FILE, 'w') as f:
        json.dump(data, f, indent=2)


SEEN_STORIES = load_seen_stories()


LOGS = deque(maxlen=20)
last_update_id = 0
last_health_ping = 0
bot_start_time = time.time()
last_run_stats = {"time": "N/A", "viewed": 0}
next_run_time = "N/A"


def send_telegram_report(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID,
                "text": message, "parse_mode": "Markdown"}
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        log_message(f"Telegram failed: {e}")


def get_status_message():
    uptime_seconds = time.time() - bot_start_time
    days, rem = divmod(uptime_seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, _ = divmod(rem, 60)
    uptime_str = f"{int(days)}d {int(hours)}h {int(minutes)}m"
    return (
        "*IG STORY AUTO-VIEWER BOT*\n\n"
        f"*Status:* RUNNING\n"
        f"*Uptime:* {uptime_str}\n"
        f"*Last Run:* {last_run_stats['time']}\n"
        f"*New Views:* {last_run_stats['viewed']}\n"
        f"*Total Saved:* {len(SEEN_STORIES)} stories (24 hours)\n"
        f"*Next Run:* {next_run_time}\n\n"
        "*Latest Logs:*\n"
        f"```\n" + "\n".join(list(LOGS)[-5:]) + "\n```"
    )


def check_telegram_commands():
    global last_update_id
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates?offset={last_update_id + 1}&timeout=5"
        r = requests.get(url, timeout=10).json()
        if r.get("ok") and r.get("result"):
            for u in r["result"]:
                last_update_id = u["update_id"]
                if u.get("message", {}).get("text") == "/status":
                    if str(u["message"]["chat"]["id"]) == TELEGRAM_CHAT_ID:
                        log_message("/status received")
                        send_telegram_report(get_status_message())
    except Exception as e:
        log_message(f"Polling error: {e}")


USER_AGENTS = [
    "Instagram 289.0.0.77.109 Android (33/13; 420dpi; 1080x2400; samsung; SM-G998B; crownlte; qcom; en_US)",
    "Instagram 301.0.0.81.110 Android (34/14; 440dpi; 1080x2408; google; Pixel 7; panther; qcom; en_US)",
    "Instagram 295.0.0.32.110 Android (33/13; 480dpi; 1080x2400; OnePlus; ONEPLUS A6013; OnePlus6T; qcom; en_GB)",
]

cl = Client(proxy=PROXY if PROXY else None)
cl.delay_range = [7, 15]
cl.set_user_agent(random.choice(USER_AGENTS))
log_message(f"User-Agent: {cl.get_settings()['user_agent'][:60]}...")


def login():
    while True:
        try:
            if SESSION_FILE.exists():
                cl.load_settings(SESSION_FILE)
                cl.get_timeline_feed()
                log_message("Login via session.")
                return
            else:
                log_message("First login...")
                cl.login(USERNAME, PASSWORD)
                cl.dump_settings(SESSION_FILE)
                log_message("Login successful! Session saved.")
                return
        except (LoginRequired, ClientError):
            log_message("Invalid session. Deleting and trying again...")
            if SESSION_FILE.exists():
                SESSION_FILE.unlink()
            time.sleep(60)
        except Exception as e:
            log_message(f"Login error: {e}")
            time.sleep(60)


login()



def get_following():
    try:
        user_id = cl.user_id or cl.user_id_from_username(USERNAME)
        all_following = cl.user_following(user_id, amount=0)
        user_ids = list(all_following.keys())
        total = len(user_ids)
        if total > MAX_FOLLOWING:
            user_ids = random.sample(user_ids, MAX_FOLLOWING)
            log_message(
                f"Total following: {total} → Random {MAX_FOLLOWING} selected.")
        else:
            log_message(f"Fetching {total} following (all).")
        return user_ids, total
    except Exception as e:
        log_message(f"Failed to fetch following: {e}")
        return [], 0


def view_stories(following_user_ids):
    global SEEN_STORIES
    viewed = 0
    now = time.time()
    for user_id in following_user_ids:
        try:
            stories = cl.user_stories(user_id)
            if not stories:
                continue
            new_pks = []
            for s in stories:
                pk = str(s.pk)
                if pk in SEEN_STORIES and now - SEEN_STORIES[pk] < 86400:
                    continue
                new_pks.append(s.pk)
                SEEN_STORIES[pk] = now
            if new_pks:
                cl.story_seen(new_pks)
                log_message(f"Viewed {len(new_pks)} NEW story")
                viewed += len(new_pks)
            time.sleep(random.uniform(3, 7))
        except Exception as e:
            log_message(f"Error user {user_id}: {e}")
        time.sleep(random.uniform(8, 15))
    save_seen_stories(SEEN_STORIES)
    return viewed


if __name__ == "__main__":
    print(BANNER)
    startup_time = time.strftime("%d %b %Y, %H:%M:%S", time.localtime())
    startup_alert = (
        "*IG STORY AUTO-VIEWER BOT*\n"
        "Status: RUNNING\n"
        f"Start Time: {startup_time} WIB\n"
        f"Interval: {CHECK_INTERVAL} seconds\n"
        f"Max Following: {MAX_FOLLOWING} accounts *(random per session)*\n"
        "Features: Anti-Double • Real-Time • Health Ping\n"
        "Monitoring: Telegram (/status)\n\n"
        "*Disclaimer:* The bot only checks 100 random accounts per session."
    )
    send_telegram_report(startup_alert)
    log_message("BOT RUNNING — Health ping active every 30 minutes")

    while True:
        try:
            following_ids, total_following = get_following()
            total_new = view_stories(following_ids) if following_ids else 0
            last_run_stats = {"time": time.strftime(
                "%d %b %Y, %H:%M:%S"), "viewed": total_new}
            LOGS.append(f"Finished: {total_new} stories viewed")
            send_telegram_report(f"Finished: {total_new} stories viewed")

        
            if time.time() - last_health_ping > 1800:
                send_telegram_report("Bot OK | Health Check")
                last_health_ping = time.time()

            wait_end = time.time() + CHECK_INTERVAL
            next_run_time = time.strftime("%H:%M:%S", time.localtime(wait_end))
            log_message(f"Waiting until {next_run_time}...")
            while time.time() < wait_end:
                check_telegram_commands()
                time.sleep(5)
        except KeyboardInterrupt:
            log_message("Bot stopped by user.")
            break
        except Exception as e:
            log_message(f"Critical error: {e}")
            time.sleep(60)
