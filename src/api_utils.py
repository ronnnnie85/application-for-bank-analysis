import logging
import os
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv

from src import loggers
from src.config import (API_EXCHANGE_URL, API_STOCKS_URL, DATA_FOLDER_NAME, FILE_USER_SETTINGS, USER_CURRENCIES,
                        USER_STOCKS)
from src.utils import get_json_file

name = os.path.splitext(os.path.basename(__file__))[0]
file_name = f"{name}.log"
logger = loggers.create_logger(name, file_name, logging.DEBUG)


def get_currency_rates(date_time: datetime) -> dict[str, float]:
    """Получает на вход дату и возвращает словарь с валютой"""
    result = {}

    fin_out_dct_path = os.path.join(os.path.dirname(__file__), f"..\\{DATA_FOLDER_NAME}", FILE_USER_SETTINGS)

    user_currencies = get_json_file(fin_out_dct_path).get(USER_CURRENCIES)

    if user_currencies:
        url = f"{API_EXCHANGE_URL}{datetime.strftime(date_time, "%Y-%m-%d")}"
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
    """Возвращает данные по ценам акций на дату"""
    result = {}

    fin_out_dct_path = os.path.join(os.path.dirname(__file__), f"..\\{DATA_FOLDER_NAME}", FILE_USER_SETTINGS)

    user_stocks = get_json_file(fin_out_dct_path).get(USER_STOCKS)

    if user_stocks:
        end_date = datetime.strftime(date_time.replace(hour=23, minute=59, second=59), "%Y-%m-%d %H:%M:%S")

        start_date = date_time - timedelta(days=10)
        start_date = datetime.strftime(start_date.replace(hour=0, minute=0, second=0), "%Y-%m-%d %H:%M:%S")

        load_dotenv()
        api_key = os.getenv("API_KEY_STOCK")
        url = API_STOCKS_URL
        parameters = {
            "interval": "1day",
            "symbol": "",
            "start_date": start_date,
            "end_date": end_date,
            "apikey": api_key,
            "dp": "2",
        }

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
