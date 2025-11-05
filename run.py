import os
import time
from pathlib import Path
from utils import setup_logger, log_message, load_config

BANNER = r"""
   _         _____  ___         _____  __  __    __   __  _____  ___  __      
  /_\  /\ /\/__   \/___\ /\   /\\_   \/__\/ / /\ \ \ / _\/__   \/___\/__\/\_/\
 //_\\/ / \ \ / /\//  // \ \ / / / /\/_\  \ \/  \/ / \ \   / /\//  // \//\_ _/
/  _  \ \_/ // / / \_//   \ V /\/ /_//__   \  /\  /  _\ \ / / / \_// _  \ / \ 
\_/ \_/\___/ \/  \___/     \_/\____/\__/    \/  \/   \__/ \/  \___/\/ \_/ \_/ 
             AUTO VIEWER + LOVE FROM FOLLOWERS - V.2.4
"""

def main_menu():
    print(BANNER)
    print("Select Mode:")
    print("===================================")
    print("  1. Auto View Story (Following)")
    print("  2. Love First Story (Followers Target)")
    print("  3. Hybrid: View (Following) + Love (Followers)")
    print("  4. Hybrid: View (Following) + View (Followers)")
    print("  5. Reset Setup")
    print("  6. Reset Login Sessions")
    print("  0. Exit")
    print("===================================")
    print("")
    return input("Choice: ").strip()

def setup_menu():
    print("\nSelect a configuration to reset:")
    print("-----------------------------------------------------")
    print("  1. Viewer / Default (resets default.env)")
    print("  2. Lover (resets lover.env)")
    print("  3. Follower Viewer (resets follower_viewer.env)")
    print("-----------------------------------------")
    print("")
    print("  0. Back to Main Menu")
    print("")
    return input("Choice: ").strip()

def reset_login_sessions():
    """Deletes all .session.json files to force re-login."""
    print("\n--- Resetting Login Sessions ---")
    config_dir = Path("configs")
    if not config_dir.exists():
        print("Configuration directory not found. Nothing to do.")
        time.sleep(2)
        return

    session_files = list(config_dir.glob("*.session.json"))
    if not session_files:
        print("No active login sessions found to reset.")
        time.sleep(2)
        return

    for f in session_files:
        f.unlink()
        log_message(f"Deleted session file: {f.name}")
    print(f"\nSuccessfully deleted {len(session_files)} session file(s).")
    print("The bot will use username/password on the next run.")
    time.sleep(3)

if __name__ == "__main__":
    setup_logger()

    from core import run_viewer, run_lover, run_hybrid_parallel, viewer_task, lover_task, follower_viewer_task
    from utils.telegram import telegram_monitor

    while True:
        choice = main_menu()
        if choice == "1":
            config = load_config(config_type='default')
            if config:
                mode_name = "Viewer"
                telegram_monitor.current_mode = mode_name
                telegram_monitor.send_startup_alert(config['TELEGRAM_TOKEN'], config['TELEGRAM_CHAT'], mode_name)
                log_message("MODE 1: VIEWER")
                run_viewer(config)
        elif choice == "2":
            targets_input = input("\nEnter target(s) for Lover mode (or leave blank to use saved): ").strip()
            config = load_config(target=targets_input, config_type='lover')
            if config:
                display_targets = ", ".join(config['TARGETS'])
                mode_name = f"Lover @{display_targets}"
                telegram_monitor.current_mode = mode_name
                telegram_monitor.send_startup_alert(config['TELEGRAM_TOKEN'], config['TELEGRAM_CHAT'], mode_name)
                log_message(f"MODE 2: {mode_name}")
                run_lover(config)
        elif choice == "3":
            print("\n--- Hybrid Mode: View (Following) + Love (Followers) ---")
            targets_input = input("Enter target(s) for Love task (or leave blank to use saved): ").strip()
            config_viewer = load_config(config_type='default')
            config_lover = load_config(target=targets_input, config_type='lover')
            if config_viewer and config_lover:
                display_targets = ", ".join(config_lover['TARGETS'])
                mode_name = f"Hybrid (View + Love @{display_targets})"
                telegram_monitor.current_mode = mode_name
                telegram_monitor.send_startup_alert(config_viewer['TELEGRAM_TOKEN'], config_viewer['TELEGRAM_CHAT'], mode_name)
                log_message(f"MODE 3: {mode_name}")
                run_hybrid_parallel([(viewer_task, config_viewer, "Viewer"), (lover_task, config_lover, "Lover")])
        elif choice == "4":
            print("\n--- Hybrid Mode: View (Following) + View (Followers) ---")
            targets_input = input("Enter target(s) for Follower View task (or leave blank to use saved): ").strip()
            config_viewer = load_config(config_type='default')
            config_follower_viewer = load_config(target=targets_input, config_type='follower_viewer')
            if config_viewer and config_follower_viewer:
                display_targets = ", ".join(config_follower_viewer['TARGETS'])
                mode_name = f"Hybrid (View + View Followers @{display_targets})"
                telegram_monitor.current_mode = mode_name
                telegram_monitor.send_startup_alert(config_viewer['TELEGRAM_TOKEN'], config_viewer['TELEGRAM_CHAT'], mode_name)
                log_message(f"MODE 4: {mode_name}")
                run_hybrid_parallel([(viewer_task, config_viewer, "Viewer"), (follower_viewer_task, config_follower_viewer, "FollowerViewer")])
        elif choice == "5":
            setup_choice = setup_menu()
            if setup_choice == "1":
                print("\n--- Resetting Viewer Mode Setup ---")
                load_config(setup_only=True, config_type='default')
                print("\nSetup complete.")
            elif setup_choice == "2":
               
                print(f"\n--- Resetting Lover config (lover.env) ---")
                load_config(setup_only=True, config_type='lover')
                print("\nSetup complete.")
            elif setup_choice == "3":
               
                print(f"\n--- Resetting Follower Viewer config (follower_viewer.env) ---")
                load_config(setup_only=True, config_type='follower_viewer')
                print("\nSetup complete.")
            else:
                print("Returning to main menu...")
                continue
        elif choice == "6":
            reset_login_sessions()
            continue
        elif choice == "0":
            break
        else:
            print("Invalid choice! Please try again.")

    log_message("Program finished.")