import json
import logging
import os
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

import pandas as pd
from pandas import DataFrame

from src import loggers
from src.config import AMOUNT_KEY, AMOUNT_ROUND_UP_KEY, CARD_NUMBER_KEY, CASHBACK_KEY, CATEGORY_KEY, STATUS_KEY

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


def get_total_amount_for_card(
    data: list[dict[str, Any]],
    expense: bool = True,
    status: str = "OK",
    except_categories: set[str] | None = None,
) -> dict[str, dict[str, Any]]:
    """Получает на вход список транзакций, признак расходов, статус.
    Возвращает словари с номерами карт и общими суммами"""
    result: dict[str, dict[str, Any]] = {}

    for transaction in data:
        card_number_str = transaction.get(CARD_NUMBER_KEY, "")
        amount_str = transaction.get(AMOUNT_ROUND_UP_KEY, "")
        amount = transaction.get(AMOUNT_KEY, "")

        if not (card_number_str and amount_str and amount):
            continue

        if except_categories and transaction.get(CATEGORY_KEY, "") in except_categories:
            continue

        card_number = get_last_digits_card_number(card_number_str)
        amount = float(amount)
        if (amount if expense else -amount) >= 0.0 or transaction.get(STATUS_KEY, "") != status:
            continue

        if result.get(card_number) is None:
            result[card_number] = {"sum": 0.0, "cashback": 0.0}
        result[card_number]["sum"] += float(amount_str)
        result[card_number]["cashback"] += float(transaction.get(CASHBACK_KEY, 0))

    logger.info("Получен словарь с номерами карт и суммами")
    return result


def get_start_date(target_date: datetime, date_period: str = "M") -> datetime:
    """Получает на вход дату и диапазон данных. Возвращает начальную дату."""
    result = target_date
    if date_period == "M":
        result = target_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif date_period == "Y":
        result = target_date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    elif date_period == "W":
        start_of_week = target_date - timedelta(days=target_date.weekday())
        result = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        result = datetime.min

    logger.info(f"Получена дата {result}")
    return result


def get_json_file(file_path: str) -> dict[str, Any]:
    """Принимает на вход путь к файлу json, возвращает словарь"""
    result: dict[str, Any] = {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                result = json.load(f)
            except json.decoder.JSONDecodeError as e:
                logger.error(f"Ошибка: {e}")
                return {}
    except FileNotFoundError as e:
        logger.error(f"Ошибка: {e}")
        return {}
    logger.info(f"Получен словарь из файла {file_path}")
    return result


def get_total_amount(
    data: list[dict[str, Any]],
    expense: bool = True,
    status: str = "OK",
    except_categories: set[str] | None = None,
) -> float:
    """Получает на вход транзакции, признак расходов, статус, возвращает сумму"""
    logger.info(f"Получена сумма {"расходов" if expense else "доходов"}")
    return sum(
        [
            float(dct.get(AMOUNT_ROUND_UP_KEY, 0))
            for dct in data
            if (dct.get(AMOUNT_KEY, 0) if expense else -dct.get(AMOUNT_KEY, 0)) < 0
            and dct.get(STATUS_KEY, "") == status
            and (dct.get(CATEGORY_KEY, "") not in except_categories if except_categories else True)
        ]
    )


def get_amount_for_categories(
    data: list[dict[str, Any]],
    expense: bool = True,
    status: str = "OK",
    num_top_cats: int = 0,
    except_categories: set[str] | None = None,
) -> dict[str, Any]:
    """Получает на вход транзакции, признак расходов, статус, кол-во топов, возвращает словарь по категориям"""
    result = {}

    operations: defaultdict = defaultdict(float)
    for transaction in data:
        category_str = transaction.get(CATEGORY_KEY, "")
        amount_str = transaction.get(AMOUNT_ROUND_UP_KEY, "")
        amount = transaction.get(AMOUNT_KEY, "")

        if not (category_str and amount_str and amount):
            continue
        amount = float(amount)
        if (amount if expense else -amount) >= 0.0 or transaction.get(STATUS_KEY, "") != status:
            continue
        if except_categories and transaction.get(CATEGORY_KEY, "") in except_categories:
            continue

        operations[category_str] += float(amount_str)

    sorted_operations = sorted(operations.items(), key=lambda x: x[1], reverse=True)

    if not num_top_cats:
        result = {key: value for key, value in sorted_operations}
    else:
        result = {key: value for key, value in sorted_operations[:num_top_cats]}

        if len(sorted_operations) > num_top_cats:
            other = sum(value for key, value in sorted_operations[num_top_cats:])
            result["Остальное"] = other
    logger.info(
        f"Получен топ{"-" + str(num_top_cats) if num_top_cats != 0 else ""} "
        f"{"расходов" if expense else "доходов"} по категориям"
    )
    return result


def read_transactions_from_excel(file_path: str) -> list[dict]:
    """Читает финансовые операции из Excel-файла и возвращает список словарей с транзакциями"""
    try:
        df = pd.read_excel(file_path)
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"Ошибка: {e}")
        return []

    transactions = df.to_dict("records")
    logger.info(f"Файл {file_path} успешно обработан")
    return transactions


def read_df_from_excel(file_path: str) -> DataFrame:
    """Читает финансовые операции из Excel-файла и возвращает dataframe с транзакциями"""
    try:
        df = pd.read_excel(file_path)
        return df
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"Ошибка: {e}")
        return pd.DataFrame()


def is_valid_datetime(datetime_str: str, format_str: str) -> bool:
    """Проверка валидности строки со временем"""
    try:
        datetime.strptime(datetime_str, format_str)
        return True
    except ValueError:
        return False