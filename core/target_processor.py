from instagrapi import Client
import time, random
from instagrapi.exceptions import UserNotFound
from pathlib import Path
from typing import Callable
from utils.logger import log_message
from utils.telegram import telegram_monitor
from .history import load_history, save_history

def process_target_followers(cl: Client, config: dict, action_function: Callable, history_prefix: str, summary_template: dict):
    """
    Generic task to process followers of a target account with a specific action.
    """
    target_username = config['TARGET']
    history_file = Path(f"data/{history_prefix}.json") # Use a single history file per mode
    HISTORY = load_history(history_file)
    
    try:
        target_id = cl.user_id_from_username(target_username)
        followers = cl.user_followers(target_id, amount=config['MAX_PROCESS'])
    except UserNotFound:
        log_message(f"Target username '@{target_username}' not found. Skipping this cycle.")
        return 0

    follower_users = list(followers.values())
    random.shuffle(follower_users)

    total_actions = 0
    detailed_logs = []
    for user in follower_users:
        if str(user.pk) in HISTORY:
            continue

        stories = cl.user_stories(user.pk)
        if stories:

            if not stories[0].user.is_private or stories[0].user.friendship_status.following:
                actions_done, log_line = action_function(cl, user, stories)
                if actions_done > 0:
                    HISTORY[str(user.pk)] = time.time()
                    log_message(log_line)
                    detailed_logs.append(f"• {log_line}")
                    total_actions += actions_done

        time.sleep(random.uniform(config[f"{summary_template['mode'].upper()}_MIN_DELAY"], config[f"{summary_template['mode'].upper()}_MAX_DELAY"]))
    
    save_history(history_file, HISTORY)

    summary_msg = summary_template['msg'].format(target=target_username, count=total_actions)
    log_message(f"{summary_template['mode'].capitalize()}: {total_actions} actions on @{target_username}'s followers.")
    telegram_monitor.logs.append(f"{summary_template['mode'].capitalize()}: {total_actions} actions from @{target_username}.")

    report = f"{summary_msg}\n\n*Details:*\n" + "\n".join(detailed_logs) if detailed_logs else summary_msg
    if total_actions > 0:
        telegram_monitor.send_message(config['TELEGRAM_TOKEN'], config['TELEGRAM_CHAT'], report)

    return total_actions