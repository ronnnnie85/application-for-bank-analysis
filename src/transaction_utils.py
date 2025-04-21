import logging
import os
from datetime import datetime
from typing import Any

from src import loggers
from src.config import AMOUNT_KEY, CATEGORY_KEY, DATE_FORMAT, DATE_TRANSACTIONS_KEY, STATUS_KEY

name = os.path.splitext(os.path.basename(__file__))[0]
file_name = f"{name}.log"
logger = loggers.create_logger(name, file_name, logging.DEBUG)


def get_transactions_for_categories(data: list[dict[str, Any]], categories: set) -> list[dict[str, Any]]:
    """Получает на вход транзакции, список категорий, возвращает список транзакций"""
    logger.info("Получен список транзакций по категориям")
    return [tx for tx in data if tx.get(CATEGORY_KEY, "") in categories]


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
