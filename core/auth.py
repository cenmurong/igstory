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
