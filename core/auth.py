from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ClientError, TwoFactorRequired, ChallengeRequired
from utils.logger import log_message
from utils.telegram import telegram_monitor

def handle_login(cl: Client, config: dict) -> bool:
    """
    Handles the login process using a persistent JSON session file.
    Prioritizes loading a session file and falls back to username/password.
    """
    username = config.get('USERNAME')
    password = config.get('PASSWORD')
    env_file_path = config.get('ENV_FILE_PATH')

    session_file = env_file_path.with_suffix('.session.json')

    try:
        if session_file.exists():
            log_message(f"Attempting to login via session file: {session_file.name}")
            cl.load_settings(session_file)
            cl.get_timeline_feed()  
            log_message("Login via session file successful!")
            return True
    except (LoginRequired, ClientError):
        log_message("Session file is invalid or expired. Deleting and attempting username/password login.")
        session_file.unlink()
    except Exception as e:
        log_message(f"Could not load session file: {e}. Attempting username/password login.")

    if not username or not password:
        log_message("CRITICAL: Username/Password not found for login!")
        return False

    try:
        log_message(f"Attempting to log in with account @{username}...")
        cl.login(username, password)
        cl.dump_settings(session_file)
        log_message(f"Login successful! Session saved to {session_file.name}")

    except (TwoFactorRequired, ChallengeRequired):
        log_message("Instagram requires a verification code to continue.")
        print("\n[!] A 6-digit code may have been sent to your registered Email or SMS.")
        print("    If you only see a 'This was me' prompt, approve it and press Enter here without typing a code.")
        verification_code = input("Enter the 6-digit code (or leave blank to retry after approval): ").strip()

        if not verification_code:
            raise ChallengeRequired("Awaiting 'This was me' approval.")
        
        cl.login(username, password, verification_code=verification_code)
        cl.dump_settings(session_file) 
    except Exception as e:
        log_message(f"Login with username/password failed: {e}")
        return False
    
   
    try:
       
        new_session_id = cl.get_cookie_value("sessionid")
        if env_file_path and new_session_id and env_file_path.exists():
            lines = [line for line in env_file_path.read_text(encoding='utf-8').splitlines() if not line.strip().startswith("SESSION_ID=")]
            lines.append(f"SESSION_ID={new_session_id}")
            env_file_path.write_text("\n".join(lines), encoding='utf-8')
            log_message(f"New SESSION_ID successfully synced to {env_file_path.name}")
        return True
    except Exception as e:
        log_message(f"Error after login while syncing SESSION_ID: {e}")
        return True 
