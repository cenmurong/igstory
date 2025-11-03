import threading
import time
import random
from instagrapi import Client
from utils.logger import log_message
from utils.telegram import telegram_monitor
from .worker import _perform_login_with_retries, USER_AGENTS

def run_task_in_thread(session_id: str, config: dict, task_function, task_name: str):
    """Runs a task function in a loop within a dedicated thread."""
    log_message(f"Thread for '{task_name}' started.")
    
    cl = Client()
    cl.private_requests = True
    cl.user_agent = random.choice(USER_AGENTS)
    proxy = config.get('PROXY')
    if proxy:
        cl.set_proxy(proxy)

    try:
        log_message(f"[{task_name}] Logging in via shared session ID...")
        cl.login_by_sessionid(session_id)
        cl.get_timeline_feed() 
    except Exception as e:
        log_message(f"CRITICAL: [{task_name}] Thread failed to log in with shared session: {e}")
        return 

    from .lover import lover_task
    from .follower_viewer import follower_viewer_task

    while True:
        try:
            
            current_config = config.copy()
            if task_function in [lover_task, follower_viewer_task] and 'TARGETS' in current_config and current_config['TARGETS']:
                selected_target = random.choice(current_config['TARGETS'])
                current_config['TARGET'] = selected_target

                log_message(f"🎯 [{task_name}] Selected target for this cycle: @{selected_target}")


            actions_count = task_function(cl, current_config) or 0

            if actions_count > 0:
                interval = random.randint(config['MIN_INTERVAL'], config['MAX_INTERVAL'])
                log_message(f"Task '{task_name}' complete ({actions_count} actions). Waiting for {interval}s (normal).")
            else:
                interval = config['SHORT_INTERVAL']
                log_message(f"Task '{task_name}' complete (0 actions). Waiting for {interval}s (short).")

            wait_end = time.time() + interval
            telegram_monitor.next_run_times[task_name] = time.strftime("%H:%M:%S", time.localtime(wait_end))
            time.sleep(interval)
        except KeyboardInterrupt:
            log_message(f"Thread '{task_name}' received stop signal.")
            break
        except Exception as e:
            log_message(f"An error occurred in '{task_name}' thread: {e}. Retrying in 60s.")
            time.sleep(60)

def run_hybrid_parallel(tasks_with_configs: list):
    """
    Runs multiple tasks in parallel, each in its own thread.
    Each task is a tuple of (task_function, config, task_name).
    """
    # Use the first task's config for the centralized login
    if not tasks_with_configs:
        log_message("No tasks provided for hybrid mode.")
        return

    login_config = tasks_with_configs[0][1]

    log_message(f"--- HYBRID MODE: INITIATING CENTRALIZED LOGIN (using config from '{login_config['ENV_FILE_PATH'].name}') ---")
    cl = Client()
    cl.private_requests = True
    cl.user_agent = random.choice(USER_AGENTS)
    log_message(f"Using User-Agent: ...{cl.user_agent[-50:]}")

    proxy = login_config.get('PROXY')
    if proxy:
        cl.set_proxy(proxy)
        log_message(f"Using proxy: {proxy}")

    if not _perform_login_with_retries(cl, login_config):
        log_message("Hybrid mode aborted due to login failure.")
        return

    session_id = cl.sessionid
    log_message("Centralized login successful. Distributing session to threads...")
    del cl 

    threads = []
    for i, (task_function, config, task_name) in enumerate(tasks_with_configs):
        thread = threading.Thread(target=run_task_in_thread, args=(session_id, config, task_function, task_name), daemon=True)
        threads.append(thread)
        thread.start()
        if i < len(tasks_with_configs) - 1:
            time.sleep(5) 

    telegram_token = login_config.get('TELEGRAM_TOKEN')
    telegram_chat_id = login_config.get('TELEGRAM_CHAT')
    for thread in threads:
        try:
            while thread.is_alive():
                telegram_monitor.check_commands(telegram_token, telegram_chat_id)
                telegram_monitor.send_health_ping(telegram_token, telegram_chat_id)
                thread.join(timeout=1.0)
        except KeyboardInterrupt:
            log_message("Main thread received stop signal. Shutting down.")
            break