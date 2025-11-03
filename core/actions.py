from instagrapi import Client

def like_first_story(cl: Client, user, stories: list) -> tuple[int, str]:
    """Action: Likes the first story."""
    if not stories:
        return 0, ""
    
    first_story = stories[0]
    cl.story_like(first_story.pk)
    log_line = f"LOVED a story from @{user.username}"
    return 1, log_line

def view_all_stories(cl: Client, user, stories: list) -> tuple[int, str]:
    """Action: Views all available stories."""
    if not stories:
        return 0, ""
        
    story_pks_to_view = [s.pk for s in stories]
    cl.story_seen(story_pks_to_view)
    log_line = f"Viewed {len(story_pks_to_view)} stories from follower @{user.username}"
    return len(story_pks_to_view), log_line