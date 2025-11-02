<<<<<<< HEAD
from instagrapi import Client
from utils.logger import log_message
from utils.telegram import telegram_monitor

def handle_login(cl: Client, config: dict) -> bool:

    session_id = config.get('SESSION_ID')
    username = config.get('USERNAME')
    password = config.get('PASSWORD')
    env_file_path = config.get('ENV_FILE_PATH')

    if session_id:
        try:
            cl.login_by_sessionid(session_id)
            log_message("Login via SESSION_ID successful!")
            return True
        except Exception as e:
            log_message(f"SESSION_ID failed or expired: {e}. Attempting login with username/password.")

    if not username or not password:
        log_message("Username/Password not found for fallback login!")
        return False

    try:
        log_message(f"Attempting to log in with account @{username}...")
        cl.login(username, password)

       
        log_message("Verifying login session...")
        cl.get_timeline_feed()
        log_message("Login successful and verified.")

        new_session_id = cl.sessionid
        if env_file_path and new_session_id and env_file_path.exists():
            lines = [line for line in env_file_path.read_text().splitlines() if not line.strip().startswith("SESSION_ID=")]
            lines.append(f"SESSION_ID={new_session_id}")
            env_file_path.write_text("\n".join(lines))
            log_message(f"New SESSION_ID successfully saved to {env_file_path.name}!")

        return True
    except Exception as e:
        error_message = str(e)
        if "checkpoint_required" in error_message.lower():
            msg = "LOGIN FAILED: Instagram requires a security check (checkpoint). Please log in via app/website to resolve it."
            log_message(msg)
            telegram_monitor.send_message(config.get('TELEGRAM_TOKEN'), config.get('TELEGRAM_CHAT'), f"⚠️ **CRITICAL: CHECKPOINT REQUIRED** ⚠️\n\n{msg}")
        else:
            log_message(f"Login with username/password failed: {e}")
        return False
=======
from instagrapi import Client
from utils.logger import log_message

def handle_login(cl: Client, config: dict) -> bool:

    session_id = config.get('SESSION_ID')
    username = config.get('USERNAME')
    password = config.get('PASSWORD')
    env_file_path = config.get('ENV_FILE_PATH')

    if session_id:
        try:
            cl.login_by_sessionid(session_id)
            log_message("Login via SESSION_ID successful!")
            return True
        except Exception as e:
            log_message(f"SESSION_ID failed or expired: {e}. Attempting login with username/password.")

    if not username or not password:
        log_message("Username/Password not found for fallback login!")
        return False

    try:
        log_message(f"Attempting to log in with account @{username}...")
        cl.login(username, password)

        new_session_id = cl.sessionid
        if env_file_path and new_session_id and env_file_path.exists():
            lines = [line for line in env_file_path.read_text().splitlines() if not line.strip().startswith("SESSION_ID=")]
            lines.append(f"SESSION_ID={new_session_id}")
            env_file_path.write_text("\n".join(lines))
            log_message(f"New SESSION_ID successfully saved to {env_file_path.name}!")

        return True
    except Exception as e:
        log_message(f"Login with username/password failed: {e}")
        return False
>>>>>>> 328ddc985d31dd6fa23c6463835628e2a959e950
