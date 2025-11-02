import json
import time
import random
import requests
from pathlib import Path
from collections import deque
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ClientError
from dotenv import load_dotenv
import os
import getpass


def interactive_setup():
    print("\n\033[93m=== AUTO STORY VIEWER BOT SETUP ===\033[0m")
    config = {}

    print("\n1. Instagram Username:")
    config['INSTAGRAM_USERNAME'] = input("   → ").strip()

    print("\n2. Instagram Password:")
    config['INSTAGRAM_PASSWORD'] = getpass.getpass("   → ")

    print("\n3. Telegram Bot Token (leave empty if not used):")
    config['TELEGRAM_BOT_TOKEN'] = input("   → ").strip()

    print("\n4. Telegram Chat ID (leave empty if not used):")
    config['TELEGRAM_CHAT_ID'] = input("   → ").strip()

    print("\n5. Check interval (seconds, default 600):")
    interval = input("   → ").strip()
    config['CHECK_INTERVAL'] = interval if interval else "600"

    print("\n6. Max Following to check (default 100):")
    max_follow = input("   → ").strip()
    config['MAX_FOLLOWING'] = max_follow if max_follow else "100"

    config['SESSION_FILE'] = "ig_session.json"
    config['VIEW_DELAY'] = "4"

    env_path = Path(".env")
    lines = [f"{k}={v}" for k, v in config.items()]
    env_path.write_text("\n".join(lines))
    print(
        f"\n\033[92mConfiguration complete! .env file has been created.\033[0m")
    log_message("Interactive setup finished.")
    return config


def load_config():
    env_path = Path(".env")
    if not env_path.exists():
        log_message(".env file not found! Starting interactive setup...")
        return interactive_setup()

    load_dotenv()
    config = {
        'INSTAGRAM_USERNAME': os.getenv('INSTAGRAM_USERNAME'),
        'INSTAGRAM_PASSWORD': os.getenv('INSTAGRAM_PASSWORD'),
        'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN'),
        'TELEGRAM_CHAT_ID': os.getenv('TELEGRAM_CHAT_ID'),
        'CHECK_INTERVAL': os.getenv('CHECK_INTERVAL', '600'),
        'VIEW_DELAY': os.getenv('VIEW_DELAY', '4'),
        'MAX_FOLLOWING': os.getenv('MAX_FOLLOWING', '100'),
        'SESSION_FILE': os.getenv('SESSION_FILE', 'ig_session.json'),
    }

    if not config['INSTAGRAM_USERNAME'] or not config['INSTAGRAM_PASSWORD']:
        log_message("Login data incomplete! Delete .env and run again.")
        env_path.unlink(missing_ok=True)
        return interactive_setup()

    return config


config = load_config()
USERNAME = config['INSTAGRAM_USERNAME']
PASSWORD = config['INSTAGRAM_PASSWORD']
SESSION_FILE = Path(config['SESSION_FILE'])
CHECK_INTERVAL = int(config['CHECK_INTERVAL'])
VIEW_DELAY = int(config['VIEW_DELAY'])
MAX_FOLLOWING = int(config['MAX_FOLLOWING'])
TELEGRAM_BOT_TOKEN = config['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = config['TELEGRAM_CHAT_ID']

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


def log_message(message):
    timestamp = time.strftime("%H:%M:%S", time.localtime())
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    LOGS.append(log_entry)



def send_telegram_report(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID,
                "text": message, "parse_mode": "Markdown"}
        requests.post(url, data=data, timeout=10)
    except:
        pass


cl = Client()
cl.delay_range = [5, 12]


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
        following = cl.user_following(user_id, amount=MAX_FOLLOWING)
        return list(following.keys())
    except Exception as e:
        log_message(f"Failed to fetch following: {e}")
        return []


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
        except:
            pass
        time.sleep(random.uniform(8, 15))
    save_seen_stories(SEEN_STORIES)
    return viewed


if __name__ == "__main__":
    log_message("AUTO STORY VIEWER BOT ACTIVE (Interactive Setup)")
    while True:
        try:
            following = get_following()
            total_new = view_stories(following) if following else 0
            msg = f"Finished: {total_new} NEW stories viewed."
            log_message(msg)
            send_telegram_report(msg)

            wait_end = time.time() + CHECK_INTERVAL
            log_message(
                f"Waiting until {time.strftime('%H:%M:%S', time.localtime(wait_end))}...")
            while time.time() < wait_end:
                time.sleep(5)
        except KeyboardInterrupt:
            log_message("Bot stopped.")
            break
        except Exception as e:
            log_message(f"Error: {e}")
            time.sleep(60)
