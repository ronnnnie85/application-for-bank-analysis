import json
import logging
import os
import re
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

from src import loggers
from src.config import (AMOUNT_KEY, AMOUNT_ROUND_UP_KEY, CARD_NUMBER_KEY, CASHBACK_KEY, CATEGORY_KEY, DATE_FORMAT,
                        DATE_TRANSACTIONS_KEY, STATUS_KEY)

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
    data: list[dict[str, Any]], expense: bool = True, status: str = "OK", except_categories: set[str] | None = None
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

        if (amount if expense else -amount) >= 0.0 or transaction.get(STATUS_KEY, "") != status:
            continue

        if result.get(card_number) is None:
            result[card_number] = {"Сумма": 0.0, "Кэшбек": 0.0}
        result[card_number]["Сумма"] += float(amount_str)
        result[card_number]["Кэшбек"] += float(transaction.get(CASHBACK_KEY, 0))

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


def get_transactions_by_date_period(
    data: list[dict[str, Any]], start_date: datetime, end_date: datetime
) -> list[dict[str, Any]]:
    """Получает на вход транзакции и даты. Возвращает транзакции за этот период"""
    result = []

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    for tx in data:
        date_tr_str = tx.get(DATE_TRANSACTIONS_KEY, "")
        if not date_tr_str:
            continue

        date_tr = datetime.strptime(date_tr_str, DATE_FORMAT)

        if start_date <= date_tr <= end_date:
            result.append(tx)
    logger.info("Получен список транзакций за период")
    return result


def top_transactions_by_amount(
    data: list[dict[str, Any]],
    expense: bool = True,
    status: str = "OK",
    num_top_cats: int = 0,
    except_categories: set[str] | None = None,
) -> list[dict]:
    """Получает на вход транзакции, признак расходов, статус, кол-во топов. Возвращает топ движений."""
    data = [
        tx
        for tx in data
        if tx.get(STATUS_KEY, "") == status
        and (tx.get(CATEGORY_KEY, "") not in except_categories if except_categories else True)
    ]
    data.sort(key=lambda x: x.get(AMOUNT_KEY, 0), reverse=not expense)
    logger.info(
        f"Получен топ{"-" + str(num_top_cats) if num_top_cats != 0 else ""} {"расходов" if expense else "доходов"}"
    )
    return data[:num_top_cats] if num_top_cats != 0 else data


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
    data: list[dict[str, Any]], expense: bool = True, status: str = "OK", except_categories: set[str] | None = None
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


def get_transactions_for_categories(data: list[dict[str, Any]], categories: set) -> list[dict[str, Any]]:
    """Получает на вход транзакции, список категорий, возвращает список транзакций"""
    logger.info("Получен список транзакций по категориям")
    return [tx for tx in data if tx.get(CATEGORY_KEY, "") in categories]


def get_cashback_categories(data: list[dict[str, Any]], percent_cashback: float) -> dict[str, Any]:
    """Получает на вход список транзакций возвращает возможный кэшбек по категориям"""
    data_cashback = [
        {**tx, AMOUNT_ROUND_UP_KEY: int(tx.get(AMOUNT_ROUND_UP_KEY, 0.0) * percent_cashback / 100)} for tx in data
    ]

    result = get_amount_for_categories(data_cashback)
    logger.info("Получены словари кэшбека по категориям")
    return result


def get_invest_amount(data: list[dict[str, Any]], limit: int) -> float:
    """Получает на вход список транзакций и лимит округления, возвращает сумму"""
    lst = [(tx.get(AMOUNT_ROUND_UP_KEY, 0) // limit + 1) * limit - tx.get(AMOUNT_ROUND_UP_KEY, 0) for tx in data]
    return float(sum(lst))


def get_simple_search(data: list[dict[str, Any]], keyword: str, search_keys: set) -> list[dict[str, Any]]:
    """Получает на вход список транзакций, запрос и множество ключей поиска, возвращает список транзакций"""
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    result = [tx for tx in data if any(pattern.search(tx[key]) for key in search_keys)]
    return result
