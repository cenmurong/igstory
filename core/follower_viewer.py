from instagrapi import Client
import time, random
from pathlib import Path
from utils.logger import log_message
from utils.telegram import telegram_monitor
from .history import load_history, save_history

FOLLOWER_SEEN_FILE = Path("data/follower_seen_stories.json")

def follower_viewer_task(cl: Client, config: dict):
    """
    Views stories from followers of a target account.
    """
    SEEN = load_history(FOLLOWER_SEEN_FILE)
    target_id = cl.user_id_from_username(config['TARGET'])
    followers = cl.user_followers(target_id, amount=config['MAX_PROCESS'])
    follower_users = list(followers.values())
    random.shuffle(follower_users)

    viewed_count = 0
    detailed_logs = []
    for user in follower_users:
        if str(user.pk) in SEEN: continue

        stories = cl.user_stories(user.pk)
        if stories:
            story_pks_to_view = [s.pk for s in stories]
            cl.story_seen(story_pks_to_view)
            SEEN[str(user.pk)] = time.time() 
            log_line = f"Viewed {len(story_pks_to_view)} stories from follower @{user.username}"
            log_message(log_line)
            detailed_logs.append(f"• {log_line}")
            viewed_count += len(story_pks_to_view)
        time.sleep(random.uniform(8, 15))
    save_history(FOLLOWER_SEEN_FILE, SEEN)

    summary_msg = f"👀 *Follower Viewer Cycle Complete*\nTarget: @{config['TARGET']}\nTotal stories viewed: {viewed_count}"
    log_message(f"Follower Viewer: {viewed_count} stories viewed from @{config['TARGET']}'s followers.")
    telegram_monitor.logs.append(f"Follower Viewer: {viewed_count} stories viewed from @{config['TARGET']}.")

    report = f"{summary_msg}\n\n*Details:*\n" + "\n".join(detailed_logs) if detailed_logs else summary_msg
    telegram_monitor.send_message(config['TELEGRAM_TOKEN'], config['TELEGRAM_CHAT'], report)