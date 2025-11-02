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
    print("  2. Love Story (Followers Target)")
    print("  3. Hybrid: View + Love")
    print("  4. Reset Setup")
    print("  0. Exit")
    print("===================================")
    print("")
    return input("Choice: ").strip()

def setup_menu():
    print("\nSelect a configuration to reset:")
    print("-----------------------------------------")
    print("  1. Mode Viewer (uses default.env)")
    print("  3. Mode Hybrid (uses default.env)")
    print("  2. Mode Lover (configs/lover_TARGET.env)")
    print("-----------------------------------------")
    print("")
    print("  0. Back to Main Menu")
    print("")
    return input("Choice: ").strip()

if __name__ == "__main__":
    setup_logger()

    from core import run_viewer, run_lover, run_hybrid
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
                config = load_config(target=target)
                if config:
                    telegram_monitor.send_startup_alert(config['TELEGRAM_TOKEN'], config['TELEGRAM_CHAT'], f"Lover @{target}")
                    log_message(f"MODE 2: LOVE → @{target}")
                    run_lover(config)
        elif choice == "3":
            config = load_config()
            if config:
                telegram_monitor.send_startup_alert(config['TELEGRAM_TOKEN'], config['TELEGRAM_CHAT'], "Hybrid")
                log_message("MODE 3: HYBRID")
                run_hybrid(config)
        elif choice == "4":
            setup_choice = setup_menu()
            if setup_choice == "1":
                print("\n--- Resetting Viewer Mode Setup ---")
                load_config(setup_only=True)
                print("\nSetup complete.")
            elif setup_choice == "3":
                print("\n--- Resetting Hybrid Mode Setup (uses default.env) ---")
                load_config(setup_only=True)
                print("\nSetup complete.")
            elif setup_choice == "2":
                target = input("\nEnter the target username whose configuration you want to reset (without @): ").strip().lstrip('@')
                if not target:
                    print("Target is empty! Canceled.")
                else:
                    print(f"\n--- Resetting Lover Mode Setup for @{target} ---")
                    load_config(target=target, setup_only=True)
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
