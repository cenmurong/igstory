import logging
from pathlib import Path
from datetime import datetime, timezone, timedelta

WIB = timezone(timedelta(hours=7))

class WIBFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=WIB)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.strftime('%H:%M:%S')

def disable_instagrapi_logs():

    for name in ["instagrapi", "urllib3", "requests"]:
        logging.getLogger(name).setLevel(logging.WARNING)

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format='............................................  %(message)s',
        datefmt='%H:%M:%S',
        handlers=[
            logging.FileHandler("bot.log", encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    formatter = WIBFormatter(fmt='[%(asctime)s] %(message)s', datefmt='%H:%M:%S')
    for handler in logging.getLogger().handlers:
        handler.setFormatter(formatter)

    disable_instagrapi_logs()

log_message = logging.info
