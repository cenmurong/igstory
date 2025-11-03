from dotenv import load_dotenv
from pathlib import Path
import os, getpass

CONFIG_DIR = Path("configs")

def create_env_interactive(env_file, target=None, config_type='lover'):
    print("\n=== CONFIGURATION SETUP ===")
    print(f"Creating new configuration file at: {env_file}")
    config = {}

    config['SESSION_ID'] = input("Instagram SESSION_ID (leave blank if none): ").strip()
    config['INSTAGRAM_USERNAME'] = input("Instagram Username (for fallback login): ").strip()
    config['INSTAGRAM_PASSWORD'] = getpass.getpass("Instagram Password (for fallback login): ")

    prompt_map = {
        'lover': "Default Target Username (for Love mode): ",
        'follower_viewer': "Default Target Username (for Follower Viewer mode): "
    }
    target_prompt = prompt_map.get(config_type, "Default Target Username: ")

    if target:
        config['TARGET_USERNAME'] = target
    else:
        config['TARGET_USERNAME'] = input(target_prompt).strip()

    config['MAX_FOLLOWING'] = input("Max following (view mode, default 100): ").strip() or "100"
    config['MAX_PROCESS'] = input("Max followers target (love/follower view mode, default 80): ").strip() or "80"
    config['TELEGRAM_BOT_TOKEN'] = input("Telegram Bot Token (leave blank if not used): ").strip()
    config['TELEGRAM_CHAT_ID'] = input("Telegram Chat ID (leave blank if not used): ").strip()
    config['CHECK_INTERVAL'] = input("Interval (seconds, default 600): ").strip() or "600"

    env_file.write_text("\n".join([f"{k}={v}" for k, v in config.items()]))
    print(f"\nFile {env_file} created successfully!")

def load_config(target=None, setup_only=False, config_type='lover'):
    CONFIG_DIR.mkdir(exist_ok=True)

    if target:
        env_file = CONFIG_DIR / f"{config_type}_{target}.env"
    else:

        env_file = CONFIG_DIR / "default.env"

    if setup_only or not env_file.exists():
        create_env_interactive(env_file, target=target, config_type=config_type)
        if setup_only:
            return None

    load_dotenv(env_file)

    return {
        'SESSION_ID': os.getenv('SESSION_ID'),
        'USERNAME': os.getenv('INSTAGRAM_USERNAME'),
        'PASSWORD': os.getenv('INSTAGRAM_PASSWORD'),

        'TARGET': target or os.getenv('TARGET_USERNAME', ''),
        'MAX_FOLLOWING': int(os.getenv('MAX_FOLLOWING', '100')),
        'MAX_PROCESS': int(os.getenv('MAX_PROCESS', '80')),
        'TELEGRAM_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN'),
        'TELEGRAM_CHAT': os.getenv('TELEGRAM_CHAT_ID'),
        'INTERVAL': int(os.getenv('CHECK_INTERVAL', '600')),
        'ENV_FILE_PATH': env_file
    }
