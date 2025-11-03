from instagrapi import Client
from .worker import run_worker
from .target_processor import process_target_followers
from .actions import like_first_story

def lover_task(cl: Client, config: dict):
    summary_template = {
        "mode": "lover",
        "msg": "💖 *Lover Cycle Complete*\nTarget: @{target}\nTotal stories loved: {count}"
    }
    return process_target_followers(
        cl, config, 
        action_function=like_first_story, 
        history_prefix="loved", 
        summary_template=summary_template
    )

def run_lover(config):
    run_worker(config, lover_task)
