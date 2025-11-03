from instagrapi import Client
from instagrapi.exceptions import LoginRequired
from pathlib import Path
import time, random, json, os
from utils.logger import log_message
from utils.telegram import telegram_monitor
from .auth import handle_login
from .history import load_history, save_history
from .worker import run_worker

SEEN_FILE = Path("data/seen_stories.json")

def load_blacklist() -> set:
    blacklist_file = Path("blacklist.txt")
    if not blacklist_file.exists():
        return set()
    return set(line.strip().lower() for line in blacklist_file.read_text().splitlines() if line.strip())

def viewer_task(cl: Client, config: dict):

    SEEN = load_history(SEEN_FILE)
    BLACKLIST = load_blacklist()
    my_user_id = cl.user_id

    following = cl.user_following(my_user_id, amount=config['MAX_FOLLOWING'])
    if BLACKLIST:
        following = {pk: user for pk, user in following.items() if user.username.lower() not in BLACKLIST}
    following_users = list(following.values())
    random.shuffle(following_users)

    viewed = 0
    detailed_logs = []
    for user in following_users:
        stories = cl.user_stories(user.pk)
        new_pks = [s.pk for s in stories if str(s.pk) not in SEEN]
        if new_pks:
            cl.story_seen(new_pks)
            for pk in new_pks: SEEN[str(pk)] = time.time()
            log_line = f"Viewed {len(new_pks)} stories from @{user.username}"
            log_message(log_line)
            detailed_logs.append(f"• {log_line}")
            viewed += len(new_pks)
        time.sleep(random.uniform(6, 12))
    save_history(SEEN_FILE, SEEN)

    summary_msg = f"✅ *Viewer Cycle Complete*\nTotal stories viewed: {viewed}"
    log_message(f"Viewer: {viewed} stories viewed.")
    telegram_monitor.last_run_stats.update({"time": time.strftime("%H:%M:%S"), "viewed": viewed, "loved": 0})
    telegram_monitor.logs.append(f"Viewer: {viewed} stories viewed.")

    report = f"{summary_msg}\n\n*Details:*\n" + "\n".join(detailed_logs) if detailed_logs else summary_msg
    telegram_monitor.send_message(config['TELEGRAM_TOKEN'], config['TELEGRAM_CHAT'], report)
    
    return viewed

def run_viewer(config):

    run_worker(config, viewer_task)
