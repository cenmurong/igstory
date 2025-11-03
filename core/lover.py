from instagrapi import Client
from instagrapi.exceptions import LoginRequired
import time, random, json
from pathlib import Path
from utils.logger import log_message
from utils.telegram import telegram_monitor
from .auth import handle_login
from .history import load_history, save_history
from .worker import run_worker

def lover_task(cl: Client, config: dict):
    target_username = config['TARGET']
    loved_file = Path(f"data/loved_{target_username}.json")
    
    LOVED = load_history(loved_file)
    target_id = cl.user_id_from_username(config['TARGET'])
    followers = cl.user_followers(target_id, amount=config['MAX_PROCESS'])
    follower_users = list(followers.values())
    random.shuffle(follower_users)

    loved = 0
    detailed_logs = []
    for user in follower_users:
        if str(user.pk) in LOVED: continue
        stories = cl.user_stories(user.pk)
        if stories:
            first = stories[0]
            cl.story_like(first.pk)
            LOVED[str(user.pk)] = time.time()
            log_line = f"LOVED a story from @{user.username}"
            log_message(log_line)
            detailed_logs.append(f"• {log_line}")
            loved += 1
        time.sleep(random.uniform(10, 18))
    save_history(loved_file, LOVED)

    summary_msg = f"💖 *Lover Cycle Complete*\nTarget: @{config['TARGET']}\nTotal stories loved: {loved}"
    log_message(f"Lover: {loved} first stories loved from @{config['TARGET']}'s followers.")
    telegram_monitor.last_run_stats.update({"time": time.strftime("%H:%M:%S"), "viewed": 0, "loved": loved})
    telegram_monitor.logs.append(f"Lover: {loved} stories loved.")

    report = f"{summary_msg}\n\n*Details:*\n" + "\n".join(detailed_logs) if detailed_logs else summary_msg
    telegram_monitor.send_message(config['TELEGRAM_TOKEN'], config['TELEGRAM_CHAT'], report)
    
    return loved

def run_lover(config):

    run_worker(config, lover_task)
