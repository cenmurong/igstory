from instagrapi import Client
from .worker import run_worker
from .target_processor import process_target_followers
from .actions import view_all_stories

def follower_viewer_task(cl: Client, config: dict):
    """
    Views stories from followers of a target account.
    """
    summary_template = {
        "mode": "follower_viewer",
        "msg": "👀 *Follower Viewer Cycle Complete*\nTarget: @{target}\nTotal stories viewed: {count}"
    }
    return process_target_followers(
        cl, config,
        action_function=view_all_stories,
        history_prefix="follower_seen",
        summary_template=summary_template
    )