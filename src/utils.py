import logging
import os
from datetime import datetime

from src import loggers

name = os.path.splitext(os.path.basename(__file__))[0]
file_name = f"{name}.log"
logger = loggers.create_logger(name, file_name, logging.DEBUG)


def get_greetings(current_date: datetime) -> str:
    """Принимает объект datetime, возвращает часть суток строкой"""
    result = ""
    hour = current_date.hour
    if 0 <= hour < 6:
        result = "Доброй ночи"
    elif hour < 12:
        result = "Доброе утро"
    elif hour < 18:
        result = "Добрый день"
    else:
        result = "Добрый вечер"
    logger.info(f"Получена часть суток {result}")
    return result