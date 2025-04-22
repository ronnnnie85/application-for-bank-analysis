import logging
import os
import re
from typing import Any

from src import loggers
from src.config import AMOUNT_ROUND_UP_KEY
from src.utils import get_amount_for_categories

name = os.path.splitext(os.path.basename(__file__))[0]
file_name = f"{name}.log"
logger = loggers.create_logger(name, file_name, logging.DEBUG)


def get_cashback_categories(data: list[dict[str, Any]], percent_cashback: float) -> dict[str, Any]:
    """Получает на вход список транзакций возвращает возможный кэшбек по категориям"""
    data_cashback = [
        {
            **tx,
            AMOUNT_ROUND_UP_KEY: int(tx.get(AMOUNT_ROUND_UP_KEY, 0.0) * percent_cashback / 100),
        }
        for tx in data
    ]

    result = get_amount_for_categories(data_cashback, except_categories={"Переводы"})
    logger.info("Получены словари кэшбека по категориям")
    return result


def get_invest_amount(data: list[dict[str, Any]], limit: int) -> float:
    """Получает на вход список транзакций и лимит округления, возвращает сумму"""
    lst = [(tx.get(AMOUNT_ROUND_UP_KEY, 0) // limit + 1) * limit - tx.get(AMOUNT_ROUND_UP_KEY, 0) for tx in data if tx.get(AMOUNT_ROUND_UP_KEY, 0) % limit != 0]
    logger.info("Получена сумма разниц после округления")
    return float(sum(lst))


def get_search_by_keyword(data: list[dict[str, Any]], keyword: str, search_keys: set, esc_symbols: bool = True) -> list[dict[str, Any]]:
    """Получает на вход список транзакций, запрос и множество ключей поиска, возвращает список транзакций"""
    key = re.escape(keyword) if esc_symbols else keyword
    pattern = re.compile(key, re.IGNORECASE)
    result = [tx for tx in data if any(pattern.search(tx[key]) for key in search_keys)]
    logger.info("Получен список транзакций по запросу")
    return result
