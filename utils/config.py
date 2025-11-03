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
        'lover': "Default Target Usernames (comma-separated for Love mode): ",
        'follower_viewer': "Default Target Usernames (comma-separated for Follower Viewer mode): "
    }
    target_prompt = prompt_map.get(config_type, "Default Target Username: ")

    if target:
        config['TARGET_USERNAME'] = target
    else:
        config['TARGET_USERNAME'] = input(target_prompt).strip()

    config['MAX_FOLLOWING'] = input("Max following (view mode, default 100): ").strip() or "100"
    config['VIEWER_MIN_DELAY'] = input("Viewer min delay between users (seconds, default 6): ").strip() or "6"
    config['VIEWER_MAX_DELAY'] = input("Viewer max delay between users (seconds, default 12): ").strip() or "12"
    config['LOVER_MIN_DELAY'] = input("Lover min delay between users (seconds, default 10): ").strip() or "10"
    config['LOVER_MAX_DELAY'] = input("Lover max delay between users (seconds, default 18): ").strip() or "18"
    config['FOLLOWER_VIEWER_MIN_DELAY'] = input("Follower Viewer min delay between users (seconds, default 8): ").strip() or "8"
    config['FOLLOWER_VIEWER_MAX_DELAY'] = input("Follower Viewer max delay between users (seconds, default 15): ").strip() or "15"
    config['MAX_PROCESS'] = input("Max followers target (love/follower view mode, default 80): ").strip() or "80"
    config['TELEGRAM_BOT_TOKEN'] = input("Telegram Bot Token (leave blank if not used): ").strip()
    config['TELEGRAM_CHAT_ID'] = input("Telegram Chat ID (leave blank if not used): ").strip()
    config['MIN_INTERVAL'] = input("Minimum interval (seconds, default 600): ").strip() or "600"
    config['MAX_INTERVAL'] = input("Maximum interval (seconds, default 700): ").strip() or "700"
    config['SHORT_INTERVAL'] = input("Short interval if no activity (seconds, default 300): ").strip() or "300"

    env_file.write_text("\n".join([f"{k}={v}" for k, v in config.items()]))
    print(f"\nFile {env_file} created successfully!")

def load_config(target=None, setup_only=False, config_type='default'):
    CONFIG_DIR.mkdir(exist_ok=True)

    # Simplified config file naming: one file per mode type
    if config_type in ['lover', 'follower_viewer']:
        env_file = CONFIG_DIR / f"{config_type}.env"
    else: # Default for viewer
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

        # Handle single target from CLI or multiple from .env
        'TARGETS': [t.strip() for t in (target or os.getenv('TARGET_USERNAME', '')).split(',') if t.strip()],
        'MAX_FOLLOWING': int(os.getenv('MAX_FOLLOWING', '100')),
        'VIEWER_MIN_DELAY': int(os.getenv('VIEWER_MIN_DELAY', '6')),
        'VIEWER_MAX_DELAY': int(os.getenv('VIEWER_MAX_DELAY', '12')),
        'LOVER_MIN_DELAY': int(os.getenv('LOVER_MIN_DELAY', '10')),
        'LOVER_MAX_DELAY': int(os.getenv('LOVER_MAX_DELAY', '18')),
        'FOLLOWER_VIEWER_MIN_DELAY': int(os.getenv('FOLLOWER_VIEWER_MIN_DELAY', '8')),
        'FOLLOWER_VIEWER_MAX_DELAY': int(os.getenv('FOLLOWER_VIEWER_MAX_DELAY', '15')),
        'MAX_PROCESS': int(os.getenv('MAX_PROCESS', '80')),
        'TELEGRAM_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN'),
        'TELEGRAM_CHAT': os.getenv('TELEGRAM_CHAT_ID'),
        'MIN_INTERVAL': int(os.getenv('MIN_INTERVAL', '600')),
        'MAX_INTERVAL': int(os.getenv('MAX_INTERVAL', '900')),
        'SHORT_INTERVAL': int(os.getenv('SHORT_INTERVAL', '300')),
        'ENV_FILE_PATH': env_file
    }
