import requests
import time
from collections import deque

class TelegramMonitor:
    def __init__(self):
        self.logs = deque(maxlen=20)
        self.last_update_id = 0
        self.last_health_ping = 0
        self.bot_start_time = time.time()
        self.last_run_stats = {"time": "N/A", "viewed": 0, "loved": 0}
        self.next_run_time = "N/A"

    def send_message(self, token, chat_id, message):
        if not token or not chat_id: return
        try:
            requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                data={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"},
                timeout=10
            )
        except Exception as e:
            print(f"CRITICAL: Gagal mengirim pesan Telegram: {e}")

    def get_status_message(self):
        uptime = time.time() - self.bot_start_time
        d, r = divmod(uptime, 86400)
        h, r = divmod(r, 3600)
        m, _ = divmod(r, 60)
        return (
            "*IG BOT STATUS*\n\n"
            f"*Status:* RUNNING\n"
            f"*Uptime:* {int(d)}d {int(h)}h {int(m)}m\n"
            f"*Last Run:* {self.last_run_stats['time']}\n"
            f"*Viewed:* {self.last_run_stats['viewed']}\n"
            f"*Loved:* {self.last_run_stats['loved']}\n"
            f"*Next Run:* {self.next_run_time}\n\n"
            "*Latest Logs:*\n"
            f"```\n" + "\n".join(list(self.logs)[-5:]) + "\n```"
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
        if time.time() - self.last_health_ping > 1800:
            self.send_message(token, chat_id, "Bot OK | Health Check")
            self.last_health_ping = time.time()

telegram_monitor = TelegramMonitor()
