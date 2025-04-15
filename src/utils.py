import logging
import os
from collections import defaultdict
from datetime import datetime
from typing import Any

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


def get_last_digits_card_number(card_number: str) -> str:
    """Получает номер карты, возвращает последние 4 цифры"""
    result = ""
    if len(card_number) >= 4:
        result = card_number[-4:]
    else:
        result = card_number
    logger.info(f"Получен номер карты {result}")
    return result


def get_total_amount(data: list[dict[str, Any]], date_time: str, date_period: str = "M") -> dict[str, float]:
    """Получает на вход список транзакций, дату окончания периода, продолжительность периода.
    Возвращает словари с номерами карт и общими суммами"""
    result = defaultdict(float)

    end_date = datetime.fromisoformat(date_time)
    start_date = datetime(end_date.year, end_date.month, 1, 0, 0, 0)

    for transaction in data:
        card_number = transaction.get("Номер карты")
        if card_number is None:
            continue

        date_tr_str = transaction.get("Дата операции", "")
        if date_tr_str == "":
            continue
        date_tr = datetime.strptime(date_tr_str, "%d.%m.%Y %H:%M:%S")
        if start_date <= date_tr <= end_date:
            result[card_number] += transaction.get("Сумма операции", 0.0)

    logger.info(f"Получен словарь с номерами карт и суммами")
    return dict(result)


