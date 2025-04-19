import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any

import requests
from dotenv import load_dotenv

from src import loggers
from src.config import (
    CARD_NUMBER_KEY,
    DATE_TRANSACTIONS_KEY,
    AMOUNT_ROUND_UP_KEY,
    AMOUNT_KEY,
    CASHBACK_KEY,
    DATE_FORMAT, USER_CURRENCIES, USER_STOCKS, STATUS_KEY,
)

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


def get_total_amount_for_card(data: list[dict[str, Any]], start_date: datetime, end_date: datetime) -> dict[str, dict[str, Any]]:
    """Получает на вход список транзакций, дату окончания периода, продолжительность периода.
    Возвращает словари с номерами карт и общими суммами"""
    result = {}

    # end_date = datetime.fromisoformat(date_time)
    # start_date = get_start_data(end_date, date_period)

    data = get_transactions_by_date_period(data, start_date, end_date)

    for transaction in data:
        card_number_str = transaction.get(CARD_NUMBER_KEY)
        amount_str = transaction.get(AMOUNT_ROUND_UP_KEY)
        amount = transaction.get(AMOUNT_KEY)

        if not (card_number_str and amount_str and amount):
            continue

        card_number = get_last_digits_card_number(card_number_str)

        if amount >= 0.0:
            continue

        if result.get(card_number) is None:
            result[card_number] = {"Сумма": 0.0, "Кэшбек": 0.0}
        result[card_number]["Сумма"] += float(amount_str)
        result[card_number]["Кэшбек"] += float(transaction.get(CASHBACK_KEY, 0))

    logger.info("Получен словарь с номерами карт и суммами")
    return result


def get_start_data(target_date: datetime, date_period: str = "M") -> datetime:
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
        date_tr_str = tx.get(DATE_TRANSACTIONS_KEY)
        if not date_tr_str:
            continue

        date_tr = datetime.strptime(date_tr_str, DATE_FORMAT)

        if start_date <= date_tr <= end_date:
            result.append(tx)
    logger.info("Получен список транзакций за период")
    return result


def top_transactions_by_amount(data: list[dict[str, Any]], start_date: datetime, end_date: datetime) -> list[dict]:
    """Получает на вход транзакции, дату и диапазон данных. Возвращает топ-5 расходов."""
    # end_date = datetime.fromisoformat(date_time)
    # start_date = get_start_data(end_date, date_period)

    data = get_transactions_by_date_period(data, start_date, end_date)
    data.sort(key=lambda x: x[AMOUNT_KEY], reverse=False)
    logger.info("Получен топ-5 расходов")
    return data[:5]


def get_json_file(file_path: str) -> dict[str, Any]:
    """Принимает на вход путь к файлу json, возвращает словарь"""
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

    return result


def get_currency_rates(date_time: datetime) -> dict[str, float]:
    """Получает на вход дату и возвращает словарь с валютой"""
    result = {}

    fin_out_dct_path = os.path.join(os.path.dirname(__file__), "..\\data", "user_settings.json")

    user_currencies = get_json_file(fin_out_dct_path).get(USER_CURRENCIES)

    if user_currencies:
        url = rf"https://api.apilayer.com/exchangerates_data/{datetime.strftime(date_time, "%Y-%m-%d")}"
        parameters = {"base": "RUB", "symbols": ",".join(user_currencies)}
        load_dotenv()
        api_key = os.getenv("API_KEY_EXCHANGE")
        headers = {"apikey": api_key}

        try:
            response = requests.get(url, headers=headers, params=parameters)
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка: {e}")
            return {}

        if response.status_code != 200:
            logger.error(f"Ошибка: Status code: {response.status_code}")
            return {}

        result = response.json().get("rates")
        if not result:
            return {}
        for key in result.keys():
            result[key] = round(1 / result[key] if result[key] != 0.0 else 0.0, 2)
        logger.info("Получен словарь с курсами валюты")
    else:
        logger.error("Ошибка: отсутствуют валюты в настройках")
    return result


def get_stock_prices(date_time: datetime) -> dict[str, float]:
    """Возвращает данные по ценам акций на текущую дату"""
    result = {}

    fin_out_dct_path = os.path.join(os.path.dirname(__file__), "..\\data", "user_settings.json")

    user_stocks = get_json_file(fin_out_dct_path).get(USER_STOCKS)

    if user_stocks:
        end_date = datetime.strftime(date_time.replace(hour=23, minute=59, second=59), "%Y-%m-%d %H:%M:%S")

        start_date = date_time - timedelta(days=10)
        start_date = datetime.strftime(start_date.replace(hour=0, minute=0, second=0), "%Y-%m-%d %H:%M:%S")

        load_dotenv()
        api_key = os.getenv("API_KEY_STOCK")
        url = rf"https://api.twelvedata.com/time_series"
        parameters = {"interval": "1day", "symbol": "", "start_date": start_date, "end_date": end_date, "apikey": api_key, "dp": "2"}

        for stock in user_stocks:
            parameters["symbol"] = stock
            try:
                response = requests.get(url, params=parameters)
            except requests.exceptions.RequestException as e:
                logger.error(f"Ошибка: {e}")
                return {}

            if response.status_code != 200:
                logger.error(f"Ошибка: Status code: {response.status_code}")
                return {}

            stocks = response.json().get("values", [])
            if stocks:
                # lst_stocks = sorted(dct_stocks.keys(), reverse=True)
                result[stock] = float(stocks[0].get("close", "0"))

    return result


def get_total_amount(data: list[dict[str, Any]], start_date: datetime, end_date: datetime, expense: bool = True) -> float:
    """Получает на вход транзакции, начальную, конечную дату, признак расходов, возвращает сумму"""
    multiplier = 1.0 if expense else -1.0
    logger.info(f"Получена сумма {"расходов" if expense else "доходов"}")
    return sum([float(dct[AMOUNT_ROUND_UP_KEY]) for dct in data if dct[AMOUNT_KEY ] * multiplier < 0 and dct[STATUS_KEY] == "OK"])
