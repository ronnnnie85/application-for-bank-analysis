import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any

from dateutil.relativedelta import relativedelta

from src import loggers
from src.services_utils import get_cashback_categories, get_invest_amount
from src.transaction_utils import get_transactions_by_date_period

name = os.path.splitext(os.path.basename(__file__))[0]
file_name = f"{name}.log"
logger = loggers.create_logger(name, file_name, logging.DEBUG)


def get_beneficial_categories(data: list[dict[str, Any]], year: str, month: str, percent_cashback: float = 5.0) -> str:
    """На вход функции поступают данные для анализа, год и месяц. На выходе — JSON с анализом,
    сколько на каждой категории можно заработать кешбэка в указанном месяце года."""
    start_date = datetime(int(year), int(month), 1)
    end_date = start_date + relativedelta(months=1) - timedelta(days=1)

    filtered_data = get_transactions_by_date_period(data, start_date, end_date)
    cashback_data = get_cashback_categories(filtered_data, percent_cashback)
    logger.info("Получен json с категориями кэшбека")
    return json.dumps(cashback_data)


def investment_bank(month: str, transactions: list[dict[str, Any]], limit: int) -> float:
    """На вход функции поступают месяц и список транзакций. На выходе возможная сумма в инвесткопилку"""
    start_date = datetime.strptime(f"{month}-01", "%Y-%m-%d")
    end_date = start_date + relativedelta(months=1) - timedelta(days=1)

    filtered_data = get_transactions_by_date_period(transactions, start_date, end_date)
    logger.info("Получена сумма для инвесткопилки")
    return get_invest_amount(filtered_data, limit)


def simple_search(transactions: list[dict[str, Any]], keyword: str) -> str:
    """На вход функции поступает список транзакция и ключевое слова.
    На выходе JSON-ответ со всеми транзакциями, содержащими запрос в описании или категории.
    """
    pass


def search_by_phone(transactions: list[dict[str, Any]]) -> str:
    """Функция возвращает JSON со всеми транзакциями, содержащими в описании мобильные номера."""
    pass


def search_person_transfer(transactions: list[dict[str, Any]]) -> str:
    """Функция возвращает JSON со всеми транзакциями, которые относятся к переводам физлицам.
    Категория такой транзакции — Переводы, а в описании есть имя и первая буква фамилии с точкой.
    """
    pass
