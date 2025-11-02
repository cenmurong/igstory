# IGStory Bot V2

   _         _____  ___         _____  __  __    __   __  _____  ___  __      
  /_\  /\ /\/__   \/___\ /\   /\\_   \/__\/ / /\ \ \ / _\/__   \/___\/__\/\_/\
 //_\\/ / \ \ / /\//  // \ \ / / / /\/_\  \ \/  \/ / \ \   / /\//  // \//\_ _/
/  _  \ \_/ // / / \_//   \ V /\/ /_//__   \  /\  /  _\ \ / / / \_// _  \ / \ 
\_/ \_/\___/ \/  \___/     \_/\____/\__/    \/  \/   \__/ \/  \___/\/ \_/ \_/ 
             AUTO VIEWER + LOVE FROM FOLLOWERS - V.2

An advanced Instagram bot for automatically viewing stories and interacting with users. Built with a robust, modular, and resilient architecture in Python.

## ✨ Features

- **Multiple Modes**:
  - **Viewer Mode**: Automatically views stories from all the accounts you follow, mimicking human behavior.
  - **Lover Mode**: A unique engagement strategy. It automatically likes the first story of each follower of a *specific target account*. This is a great way to gain visibility among users with similar interests.
  - **Hybrid Mode**: Runs both Viewer and Lover tasks sequentially in a single, efficient cycle.
- **Robust Login System**: Prioritizes `SESSION_ID` for stable, long-running sessions with an automatic fallback to username/password.
- **Automatic Session Renewal**: If a session expires, the bot automatically re-logs in and updates the configuration file with the new `SESSION_ID`.
- **Comprehensive Telegram Monitoring**:
  - Get real-time bot status with the `/status` command.
  - Receive startup alerts and periodic "health pings".
  - Get a summary notification after each operational cycle.
- **Smart Error Handling**: Intelligently handles common issues like session expiries and network connection errors to ensure maximum uptime.
- **Dynamic Configuration**: Manages separate configurations for each mode and target in the `configs/` directory, allowing for different accounts or settings per task.
- **Interactive Setup**: A user-friendly command-line interface guides you through the initial setup process.
- **Anti-Detection Measures**:
  - Randomized delays between actions to mimic human behavior.
  - User-Agent rotation on each startup.

## 📋 Requirements

- Python 3.7+
- Dependencies listed in `requirements.txt`:
  - `instagrapi`
  - `python-dotenv`
  - `requests`

## 🚀 Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/cenmurong/igstory
    cd igstory
    ```

2.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## ▶️ Usage

1.  **Run the bot:**
    ```bash
    python run.py
    ```

2.  **First-Time Setup:**
    On the first run for any mode, the bot will launch an interactive setup wizard. You will be prompted to enter your Instagram credentials, Telegram details, and other settings.

    - **`SESSION_ID`**: It's highly recommended to provide this for a more stable login. You can leave it blank to log in with a username/password, and the bot will automatically save the new `SESSION_ID` for future use.

3.  **Main Menu:**
    After setup, you will be presented with the main menu to choose an operational mode:
    - `1. Auto View Story (Following)`: Starts the viewer mode.
    - `2. Love Story (Followers Target)`: Starts the lover mode for a specific target.
    - `3. Hybrid: View + Love`: Runs both viewer and lover tasks in one cycle.
    - `4. Reset Setup`: Allows you to re-run the setup for a specific mode.
    - `0. Exit`: Shuts down the bot.

## ⚙️ Configuration

All configuration files are stored as `.env` files inside the `configs/` directory.

- **`configs/default.env`**: Used for the **Viewer** mode.
- **`configs/lover_<target_username>.env`**: A unique file is created for each target in **Lover** mode (e.g., `lover_instagram.env`).

### Key Variables

- `SESSION_ID`: Your Instagram session cookie. The most reliable way to log in.
- `INSTAGRAM_USERNAME`: Your username, used as a fallback if `SESSION_ID` is missing or invalid.
- `INSTAGRAM_PASSWORD`: Your password, used for fallback login.
- `TARGET_USERNAME`: The target account for Lover mode.
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot's API token.
- `TELEGRAM_CHAT_ID`: The chat ID where notifications will be sent.
- `CHECK_INTERVAL`: The delay in seconds between each operational cycle.

## 🤖 Telegram Integration

The bot provides powerful monitoring capabilities through Telegram.

- **Startup Alert**: Notifies you when the bot starts and in which mode.
- **Cycle Summary**: Sends a brief report after each cycle (e.g., "Viewer: 42 stories viewed.").
- **Health Ping**: Sends a "Bot OK" message every 30 minutes to confirm the bot is still alive.
- **/status Command**: Send this command to your bot at any time to get a detailed, real-time status report including uptime, last run stats, and recent logs.

## 📂 Project Structure

```
igstory/
├── configs/              # Stores all .env configuration files
├── core/                 # Core application logic
│   ├── auth.py           # Handles login and session management
│   ├── history.py        # Manages seen/loved history
│   ├── lover.py          # Task logic for "Lover" mode
│   ├── viewer.py         # Task logic for "Viewer" mode
│   └── worker.py         # Generic worker that runs the main bot loop
├── utils/                # Utility modules
│   ├── config.py         # Manages loading and creating configs
│   └── telegram.py       # Handles all Telegram communication
├── run.py                # Main entry point of the application
├── bot.log               # Log file for bot activities
└── README.md             # This file
```

---
## Connect With Me

<p>
  <a href="https://x.com/cenmurong"><img src="https://img.shields.io/badge/X-000000?style=for-the-badge&logo=x&logoColor=white" /></a>
  <a href="https://discord.com/users/451101979331002370"><img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" /></a>
  <a href="https://instagram.com/asaptrfr"><img src="https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white" /></a>
</p>

> **Disclaimer:** This bot is for educational purposes only. Automating Instagram activity may be against their terms of service. Use at your own risk.