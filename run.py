import os
import time
from utils import setup_logger, log_message, load_config

BANNER = r"""
   _         _____  ___         _____  __  __    __   __  _____  ___  __      
  /_\  /\ /\/__   \/___\ /\   /\\_   \/__\/ / /\ \ \ / _\/__   \/___\/__\/\_/\
 //_\\/ / \ \ / /\//  // \ \ / / / /\/_\  \ \/  \/ / \ \   / /\//  // \//\_ _/
/  _  \ \_/ // / / \_//   \ V /\/ /_//__   \  /\  /  _\ \ / / / \_// _  \ / \ 
\_/ \_/\___/ \/  \___/     \_/\____/\__/    \/  \/   \__/ \/  \___/\/ \_/ \_/ 
             AUTO VIEWER + LOVE FROM FOLLOWERS - V.2
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
    print("  0. Exit")
    print("===================================")
    print("")
    return input("Choice: ").strip()

def setup_menu():
    print("\nSelect a configuration to reset:")
    print("-----------------------------------------------------")
    print("  1. Viewer / Default (resets default.env)")
    print("  2. Lover (resets lover_TARGET.env)")
    print("  3. Follower Viewer (resets follower_viewer_TARGET.env)")
    print("-----------------------------------------")
    print("")
    print("  0. Back to Main Menu")
    print("")
    return input("Choice: ").strip()

if __name__ == "__main__":
    setup_logger()

    from core import run_viewer, run_lover, run_hybrid_parallel, viewer_task, lover_task, follower_viewer_task
    from utils.telegram import telegram_monitor

    while True:
        choice = main_menu()
        if choice == "1":
            config = load_config()
            if config:
                telegram_monitor.send_startup_alert(config['TELEGRAM_TOKEN'], config['TELEGRAM_CHAT'], "Viewer")
                log_message("MODE 1: VIEWER")
                run_viewer(config)
        elif choice == "2":
            target = input("\nEnter target username (without @): ").strip().lstrip('@')
            if not target:
                print("Target is empty! Canceled.")
            else:
                config = load_config(target=target, config_type='lover')
                if config:
                    telegram_monitor.send_startup_alert(config['TELEGRAM_TOKEN'], config['TELEGRAM_CHAT'], f"Lover @{target}")
                    log_message(f"MODE 2: LOVE → @{target}")
                    
                    run_lover(config) 
        elif choice == "3":
            print("\n--- Hybrid Mode: View (Following) + Love (Followers) ---")
            target = input("Enter target username for Love task (without @): ").strip().lstrip('@')
            if not target:
                print("Target is empty! Canceled.")
            else:
                config_viewer = load_config()
                config_lover = load_config(target=target, config_type='lover')
                if config_viewer and config_lover:
                    mode_name = f"Hybrid (View + Love @{target})"
                    telegram_monitor.send_startup_alert(config_viewer['TELEGRAM_TOKEN'], config_viewer['TELEGRAM_CHAT'], mode_name)
                    log_message(f"MODE 3: {mode_name}")
                    run_hybrid_parallel([(viewer_task, config_viewer, "Viewer"), (lover_task, config_lover, "Lover")])
        elif choice == "4":
            print("\n--- Hybrid Mode: View (Following) + View (Followers) ---")
            target = input("Enter target username for Follower View task (without @): ").strip().lstrip('@')
            if not target:
                print("Target is empty! Canceled.")
            else:
                config_viewer = load_config()
                config_follower_viewer = load_config(target=target, config_type='follower_viewer')
                if config_viewer and config_follower_viewer:
                    mode_name = f"Hybrid (View + View Followers @{target})"
                    telegram_monitor.send_startup_alert(config_viewer['TELEGRAM_TOKEN'], config_viewer['TELEGRAM_CHAT'], mode_name)
                    log_message(f"MODE 4: {mode_name}")
                    run_hybrid_parallel([(viewer_task, config_viewer, "Viewer"), (follower_viewer_task, config_follower_viewer, "FollowerViewer")])
        elif choice == "5":
            setup_choice = setup_menu()
            if setup_choice == "1":
                print("\n--- Resetting Viewer Mode Setup ---")
                load_config(setup_only=True)
                print("\nSetup complete.")
            elif setup_choice == "2":
                target = input("\nEnter the target username whose configuration you want to reset (without @): ").strip().lstrip('@')
                if not target:
                    print("Target is empty! Canceled.")
                else:
                    print(f"\n--- Resetting Lover config for @{target} ---")
                    load_config(target=target, setup_only=True, config_type='lover')
                    print("\nSetup complete.")
            elif setup_choice == "3":
                target = input("\nEnter the target username whose configuration you want to reset (without @): ").strip().lstrip('@')
                if not target:
                    print("Target is empty! Canceled.")
                else:
                    print(f"\n--- Resetting Follower Viewer config for @{target} ---")
                    load_config(target=target, setup_only=True, config_type='follower_viewer')
                    print("\nSetup complete.")
            else:
                print("Returning to main menu...")
                continue
        elif choice == "0":
            break
        else:
            print("Invalid choice! Please try again.")

        print("\nBot cycle finished, returning to main menu...")
        time.sleep(2)

    log_message("Program finished.")