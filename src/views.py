import json
import logging
import os
from datetime import datetime
from typing import Any

from src import loggers
from src.api_utils import get_currency_rates, get_stock_prices
from src.config import (
    AMOUNT_ROUND_UP_KEY,
    CATEGORY_KEY,
    DATA_FOLDER_NAME,
    DATE_TRANSACTIONS_KEY,
    DESCRIPTION_KEY,
    FILE_OPERATIONS,
)
from src.transaction_utils import (
    get_transactions_by_date_period,
    get_transactions_for_categories,
    top_transactions_by_amount,
)
from src.utils import (
    get_amount_for_categories,
    get_greetings,
    get_start_date,
    get_total_amount,
    get_total_amount_for_card,
    read_transactions_from_excel,
)

name = os.path.splitext(os.path.basename(__file__))[0]
file_name = f"{name}.log"
logger = loggers.create_logger(name, file_name, logging.DEBUG)


def get_data_main(date_time: str) -> str:
    """Принимает на вход дату и время и возвращает json с данными"""
    result: dict[str, Any] = {}

    filename = os.path.join(os.path.dirname(__file__), f"../{DATA_FOLDER_NAME}", FILE_OPERATIONS)
    transactions = read_transactions_from_excel(filename)

    end_date = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    start_date = get_start_date(end_date)
    filtered_data = get_transactions_by_date_period(transactions, start_date, end_date)

    now_date = datetime.now()

    result["greeting"] = get_greetings(now_date)

    card_data = get_total_amount_for_card(filtered_data)
    result["cards"] = [
        {
            "last_digits": key,
            "total_spent": round(value.get("sum", 0.0), 2),
            "cashback": round(value.get("cashback", 0.0), 2),
        }
        for key, value in card_data.items()
    ]

    top_transactions = top_transactions_by_amount(filtered_data, num_top_cats=5)
    result["top_transactions"] = [
        {
            "date": datetime.strftime(datetime.strptime(tx.get(DATE_TRANSACTIONS_KEY, ""), "%d.%m.%Y %H:%M:%S"), "%d.%m.%Y"),
            "amount": round(tx.get(AMOUNT_ROUND_UP_KEY, 0.0), 2),
            "category": tx.get(CATEGORY_KEY, ""),
            "description": tx.get(DESCRIPTION_KEY, ""),
        }
        for tx in top_transactions
    ]

    currency_rates = get_currency_rates(now_date)
    result["currency_rates"] = [{"currency": key, "rate": round(value, 2)} for key, value in currency_rates.items()]

    stock_prices = get_stock_prices(now_date)
    result["stock_prices"] = [{"stock": key, "price": round(value, 2)} for key, value in stock_prices.items()]

    try:
        data_json = json.dumps(result)
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        data_json = json.dumps({})
    logger.info("Получен json для главной страницы")
    return data_json


def get_data_events(date_time: str, date_period: str = "M") -> str:
    """Принимает строку с датой и необязательный параметр диапазон.
    Возвращает json с данными"""
    result: dict[str, Any] = {}

    filename = os.path.join(os.path.dirname(__file__), f"../{DATA_FOLDER_NAME}", FILE_OPERATIONS)
    transactions = read_transactions_from_excel(filename)

    end_date = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    start_date = get_start_date(end_date, date_period)
    filtered_data = get_transactions_by_date_period(transactions, start_date, end_date)

    result["expenses"] = {}
    result["expenses"]["total_amount"] = get_total_amount(filtered_data)

    categories_expenses = get_amount_for_categories(filtered_data, num_top_cats=7)
    result["expenses"]["main"] = [
        {"category": key, "amount": round(value, 2)} for key, value in categories_expenses.items()
    ]

    expense_cats = get_transactions_for_categories(filtered_data, {"Наличные", "Переводы"})
    transfers_cash = get_amount_for_categories(expense_cats)
    result["expenses"]["transfers_and_cash"] = [
        {"category": key, "amount": round(value, 2)} for key, value in transfers_cash.items()
    ]

    result["income"] = {}
    result["income"]["total_amount"] = get_total_amount(filtered_data, expense=False)

    categories_incomes = get_amount_for_categories(filtered_data, expense=False)
    result["income"]["main"] = [
        {"category": key, "amount": round(value, 2)} for key, value in categories_incomes.items()
    ]

    now_date = datetime.now()
    currency_rates = get_currency_rates(now_date)
    result["currency_rates"] = [{"currency": key, "rate": round(value, 2)} for key, value in currency_rates.items()]

    stock_prices = get_stock_prices(now_date)
    result["stock_prices"] = [{"stock": key, "price": round(value, 2)} for key, value in stock_prices.items()]

    try:
        data_json = json.dumps(result)
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        data_json = json.dumps({})
    logger.info("Получен json для страницы События")
    return data_json
