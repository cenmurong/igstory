import logging
from pathlib import Path
from datetime import datetime, timezone, timedelta

WIB = timezone(timedelta(hours=7))

class WIBFormatter(logging.Formatter):

    def formatTime(self, record, datefmt=None):
        dt = datetime.now(WIB)
        return dt.strftime(datefmt or self.default_time_format)

def setup_logger():

    for name in ["instagrapi", "urllib3", "requests"]:
        logging.getLogger(name).setLevel(logging.WARNING)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    formatter = WIBFormatter(fmt='[%(asctime)s] %(message)s', datefmt='%H:%M:%S')
    for handler in [logging.FileHandler("bot.log", encoding='utf-8'), logging.StreamHandler()]:
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)

log_message = logging.info

from .config import load_config
from .telegram import telegram_monitor

__all__ = ['setup_logger', 'log_message', 'load_config', 'telegram_monitor']
