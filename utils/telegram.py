import requests
import time
from collections import deque
import platform
import sys
import psutil

class TelegramMonitor:
    def __init__(self):
        self.logs = deque(maxlen=20)
        self.last_update_id = 0
        self.last_health_ping = 0
        self.bot_start_time = time.time()
        self.last_run_stats = {"time": "N/A", "viewed": 0, "loved": 0}
        self.current_mode = "Initializing..."
        self.next_run_times = {} # Changed from string to dict

    def send_message(self, token, chat_id, message):
        if not token or not chat_id: return
        try:
            requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                data={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"},
                timeout=10
            )
        except Exception as e:
            print(f"CRITICAL: Failed to send Telegram message: {e}")

    def get_status_message(self):
        uptime = time.time() - self.bot_start_time
        d, r = divmod(uptime, 86400)
        h, r = divmod(r, 3600)
        m, _ = divmod(r, 60)

        # Get next run time, handling single and multi-threaded modes
        if not self.next_run_times:
            next_run_display = "Waiting..."
        elif len(self.next_run_times) == 1:
            next_run_display = list(self.next_run_times.values())[0]
        else:
            # For hybrid mode, show individual next runs
            next_run_display = "\n  ".join([f"• {name}: {t}" for name, t in self.next_run_times.items()])

        # Get system stats
        py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        os_info = platform.system()
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent

        return (
            f"🤖 IG BOT STATUS\n\n"
            f"Bot Health\n"
            f"  🟢 Status: `RUNNING`\n"
            f"  ⏱️ Uptime: `{int(d)}d {int(h)}h {int(m)}m`\n"
            f"  ▶️ Mode: `{self.current_mode}`\n\n"
            f"Cycle Info\n"
            f"  🔄 Last Run: `{self.last_run_stats['time']}`\n"
            f"  👀 Viewed: `{self.last_run_stats['viewed']}`\n"
            f"  💖 Loved: `{self.last_run_stats['loved']}`\n"
            f"  ⏭️ Next Run:*\n  `{next_run_display}`\n\n"
            f"System Info\n"
            f"  🐍 Python: `{py_version}`\n"
            f"  💻 Platform: `{os_info}`\n"
            f"  🧠 *CPU Usage: `{cpu_usage}%`\n"
            f"  💾 RAM Usage: `{ram_usage}%`\n\n"
            f"Latest Logs\n"
            f"```\n" + "\n".join(list(self.logs)[-7:]) + "\n```"
        )

    def check_commands(self, token, chat_id):
        if not token or not chat_id: return
        try:
            url = f"https://api.telegram.org/bot{token}/getUpdates?offset={self.last_update_id + 1}&timeout=5"
            r = requests.get(url, timeout=10).json()
            if r.get("ok") and r.get("result"):
                for u in r["result"]:
                    self.last_update_id = u["update_id"]
                    text = u.get("message", {}).get("text", "")
                    sender = str(u["message"]["chat"]["id"])
                    if sender == chat_id and text == "/status":
                        from . import log_message
                        log_message("/status received")
                        self.send_message(token, chat_id, self.get_status_message())
        except Exception as e:
            print(f"CRITICAL: Telegram poll error: {e}")

    def send_startup_alert(self, token, chat_id, mode):
        if not token or not chat_id: return
        msg = (
            f"*BOT STARTED*\n"
            f"Mode: {mode}\n"
            f"Time: {time.strftime('%H:%M:%S')} (GMT+7)\n"
            "Use /status to monitor"
        )
        self.send_message(token, chat_id, msg)

    def send_health_ping(self, token, chat_id):
        if time.time() - self.last_health_ping > 1800:  # 30 minutes
            self.send_message(token, chat_id, "Bot OK | Health Check")
            self.last_health_ping = time.time()

telegram_monitor = TelegramMonitor()