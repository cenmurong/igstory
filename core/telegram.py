import requests
import time
from collections import deque

LOGS = deque(maxlen=20)
last_update_id = 0
last_health_ping = 0
bot_start_time = time.time()
last_run_stats = {"time": "N/A", "viewed": 0, "loved": 0}
next_run_time = "N/A"

def send_telegram(token, chat_id, message):
    if not token or not chat_id: return
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"},
            timeout=10
        )
    except: pass

def get_status_message():
    from datetime import datetime
    uptime = time.time() - bot_start_time
    d, r = divmod(uptime, 86400)
    h, r = divmod(r, 3600)
    m, _ = divmod(r, 60)
    return (
        "*IG BOT STATUS*\n\n"
        f"*Status:* RUNNING\n"
        f"*Uptime:* {int(d)}d {int(h)}h {int(m)}m\n"
        f"*Last Run:* {last_run_stats['time']}\n"
        f"*Viewed:* {last_run_stats['viewed']}\n"
        f"*Loved:* {last_run_stats['loved']}\n"
        f"*Next Run:* {next_run_time}\n\n"
        "*Latest Logs:*\n"
        f"```\n" + "\n".join(list(LOGS)[-5:]) + "\n```"
    )

def check_telegram_commands(token, chat_id):
    global last_update_id
    if not token or not chat_id: return
    try:
        url = f"https://api.telegram.org/bot{token}/getUpdates?offset={last_update_id + 1}&timeout=5"
        r = requests.get(url, timeout=10).json()
        if r.get("ok") and r.get("result"):
            for u in r["result"]:
                last_update_id = u["update_id"]
                text = u.get("message", {}).get("text", "")
                sender = str(u["message"]["chat"]["id"])
                if sender == chat_id and text == "/status":
                    from utils.logger import log_message
                    log_message("/status received")
                    send_telegram(token, chat_id, get_status_message())
    except Exception as e:
        from utils.logger import log_message
        log_message(f"Telegram poll error: {e}")

def send_startup_alert(token, chat_id, mode):
    if not token or not chat_id: return
    msg = (
        f"*BOT STARTED*\n"
        f"Mode: {mode}\n"
        f"Time: {time.strftime('%H:%M:%S')} WIB\n"
        "Use /status to monitor"
    )
    send_telegram(token, chat_id, msg)

def send_health_ping(token, chat_id):
    global last_health_ping
    if time.time() - last_health_ping > 1800:
        send_telegram(token, chat_id, "Bot OK | Health Check")
        last_health_ping = time.time()
