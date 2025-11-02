from instagrapi import Client
from instagrapi.exceptions import LoginRequired
from pathlib import Path
import time, random, json, os
from utils.logger import log_message
from utils.telegram import telegram_monitor
from .auth import handle_login
from .history import load_history, save_history
from .worker import run_worker

SEEN_FILE = Path("seen_stories.json")

def viewer_task(cl: Client, config: dict):

    SEEN = load_history(SEEN_FILE)
    my_user_id = cl.user_id

    following = cl.user_following(my_user_id, amount=config['MAX_FOLLOWING'])
    following_users = list(following.values())
    random.shuffle(following_users)

    viewed = 0
    for user in following_users:
        stories = cl.user_stories(user.pk)
        new_pks = [s.pk for s in stories if str(s.pk) not in SEEN]
        if new_pks:
            cl.story_seen(new_pks)
            for pk in new_pks: SEEN[str(pk)] = time.time()
            log_message(f"Viewed {len(new_pks)} stories from @{user.username}")
            viewed += len(new_pks)
        time.sleep(random.uniform(6, 12))
    save_history(SEEN_FILE, SEEN)

    msg = f"Viewer: {viewed} stories viewed."
    log_message(msg)
    telegram_monitor.last_run_stats.update({"time": time.strftime("%H:%M:%S"), "viewed": viewed, "loved": 0})
    telegram_monitor.logs.append(msg)
    telegram_monitor.send_message(config['TELEGRAM_TOKEN'], config['TELEGRAM_CHAT'], msg)

def run_viewer(config):

    run_worker(config, viewer_task)
