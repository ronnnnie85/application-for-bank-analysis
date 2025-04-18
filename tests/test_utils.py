import json
from datetime import datetime
from unittest.mock import patch, mock_open

import pytest
import requests

from src.utils import (
    get_greetings,
    get_last_digits_card_number,
    get_total_amount_for_card,
    get_start_data,
    get_transactions_by_date_period, top_transactions_by_amount, get_currency_rates, get_json_file, get_stock_prices,
)


@pytest.mark.parametrize(
    "date, expected",
    [
        (datetime(2025, 4, 15, 1), "Доброй ночи"),
        (datetime(2025, 4, 15, 6), "Доброе утро"),
        (datetime(2025, 4, 15, 17, 59, 59), "Добрый день"),
        (datetime(2025, 4, 15, 19), "Добрый вечер"),
    ],
)
def test_get_greetings(date, expected):
    assert get_greetings(date) == expected


@pytest.mark.parametrize("card_number, expected", [("1234567887654321", "4321"), ("234", "234"), ("", "")])
def test_get_last_digits_card_number(card_number, expected):
    assert get_last_digits_card_number(card_number) == expected


def test_get_total_amount_for_card(list_transactions):
    assert get_total_amount_for_card(list_transactions, datetime(2018, 1, 1), datetime(2018, 1, 31)) == {
        "7197": {"Сумма": 410.06, "Кэшбек": 7.0}
    }


@pytest.mark.parametrize(
    "date, period, expected",
    [
        (datetime(2024, 1, 31), "M", datetime(2024, 1, 1)),
        (datetime(2024, 1, 31), "Y", datetime(2024, 1, 1)),
        (datetime(2024, 1, 31), "W", datetime(2024, 1, 29)),
        (datetime(2024, 1, 31), "ALL", datetime(1, 1, 1)),
    ],
)
def test_get_start_data(date, period, expected):
    assert get_start_data(date, period) == expected


def test_get_transactions_by_date_period(list_transactions, tr_by_period):
    assert get_transactions_by_date_period(list_transactions, datetime(2018, 1, 3), datetime(2018, 1, 10)) == tr_by_period


def test_get_transactions_by_date_period_rev(tr_by_period):
    assert get_transactions_by_date_period([{}], datetime(2018, 1, 10), datetime(2018, 1, 3)) == []


def test_top_transactions_by_amount(list_transactions):
    assert top_transactions_by_amount(list_transactions, datetime(2018, 1, 1), datetime(2018, 1, 31)) == [
        {
            "Дата операции": "01.01.2018 12:49:53",
            "Дата платежа": "01.01.2018",
            "Номер карты": None,
            "Статус": "OK",
            "Сумма операции": -3000.0,
            "Валюта операции": "RUB",
            "Сумма платежа": -3000.0,
            "Валюта платежа": "RUB",
            "Кэшбэк": None,
            "Категория": "Переводы",
            "MCC": None,
            "Описание": "Линзомат ТЦ Юность",
            "Бонусы (включая кэшбэк)": 0,
            "Округление на инвесткопилку": 0,
            "Сумма операции с округлением": 3000.0,
        },
        {
            "Дата операции": "01.01.2018 20:27:51",
            "Дата платежа": "04.01.2018",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма операции": -316.0,
            "Валюта операции": "RUB",
            "Сумма платежа": -316.0,
            "Валюта платежа": "RUB",
            "Кэшбэк": None,
            "Категория": "Красота",
            "MCC": 5977.0,
            "Описание": "OOO Balid",
            "Бонусы (включая кэшбэк)": 6,
            "Округление на инвесткопилку": 0,
            "Сумма операции с округлением": 316.0,
        },
        {
            "Дата операции": "03.01.2018 15:03:35",
            "Дата платежа": "04.01.2018",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма операции": -73.06,
            "Валюта операции": "RUB",
            "Сумма платежа": -73.06,
            "Валюта платежа": "RUB",
            "Кэшбэк": None,
            "Категория": "Супермаркеты",
            "MCC": 5499.0,
            "Описание": "Magazin 25",
            "Бонусы (включая кэшбэк)": 1,
            "Округление на инвесткопилку": 0,
            "Сумма операции с округлением": 73.06,
        },
        {
            "Дата операции": "03.01.2018 14:55:21",
            "Дата платежа": "05.01.2018",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма операции": -21.0,
            "Валюта операции": "RUB",
            "Сумма платежа": -21.0,
            "Валюта платежа": "RUB",
            "Кэшбэк": None,
            "Категория": "Красота",
            "MCC": 5977.0,
            "Описание": "OOO Balid",
            "Бонусы (включая кэшбэк)": 0,
            "Округление на инвесткопилку": 0,
            "Сумма операции с округлением": 21.0,
        },
        {
            "Дата операции": "23.01.2018 14:55:21",
            "Дата платежа": "25.01.2018",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма операции": 21.0,
            "Валюта операции": "RUB",
            "Сумма платежа": 21.0,
            "Валюта платежа": "RUB",
            "Кэшбэк": None,
            "Категория": "Красота",
            "MCC": 5977.0,
            "Описание": "OOO Balid",
            "Бонусы (включая кэшбэк)": 0,
            "Округление на инвесткопилку": 0,
            "Сумма операции с округлением": 21.0,
        },
    ]


@patch("src.utils.get_json_file")
def test_get_currency_rates(mock_file, user_settings, test_date):
    mock_file.return_value = user_settings
    with patch("src.utils.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"rates": {"EUR": 0.014409, "GBP": 0.012201}}
        assert get_currency_rates(test_date) == {"EUR": round(1 / 0.014409, 2), "GBP": round(1 / 0.012201, 2)}


@patch("src.utils.get_json_file")
def test_get_currency_rates_empty_settings(mock_file, test_date):
    mock_file.return_value = {}
    assert get_currency_rates(test_date) == {}


@patch("src.utils.get_json_file")
def test_get_currency_rates_err_req(mock_file, user_settings, test_date):
    mock_file.return_value = user_settings
    with patch("src.utils.requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException
        assert get_currency_rates(test_date) == {}


@patch("src.utils.get_json_file")
def test_get_currency_rates_err_status_code(mock_file, user_settings, test_date):
    mock_file.return_value = user_settings
    with patch("src.utils.requests.get") as mock_get:
        mock_get.return_value.status_code = 400
        assert get_currency_rates(test_date) == {}


@patch("src.utils.get_json_file")
def test_get_currency_rates_res_empty(mock_file, user_settings, test_date):
    mock_file.return_value = user_settings
    with patch("src.utils.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {}
        assert get_currency_rates(test_date) == {}


@patch("src.utils.open")
def test_get_json_file_err_open(mock_file):
    mock_file.side_effect = FileNotFoundError
    assert get_json_file("") == {}


@patch("src.utils.json.load")
@patch("src.utils.open")
def test_get_json_file_err_decode(mock_file, mock_json):
    mock_json.side_effect = json.decoder.JSONDecodeError("", "", 0)
    assert get_json_file("") == {}

def test_get_json_file(user_settings):
    test_data = json.dumps(user_settings)
    with patch("src.utils.open", new_callable=mock_open, read_data=test_data) as mock_file:
        assert get_json_file("") == user_settings


@patch("src.utils.get_json_file")
@patch("src.utils.requests.get")
def test_get_stock_prices(mock_get, mock_json, user_settings, stocks_response, test_date):
    mock_json.return_value = user_settings
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = stocks_response
    assert get_stock_prices(test_date) == {"AAPL": 196.98, "AMZN": 196.98}


@patch("src.utils.get_json_file")
@patch("src.utils.requests.get")
def test_get_stock_prices_exception(mock_get, mock_json, user_settings, test_date):
    mock_json.return_value = user_settings
    mock_get.side_effect = requests.exceptions.RequestException
    assert get_stock_prices(test_date) == {}


@patch("src.utils.get_json_file")
@patch("src.utils.requests.get")
def test_get_stock_prices_status_code(mock_get, mock_json, user_settings, test_date):
    mock_json.return_value = user_settings
    mock_get.mock_get.return_value.status_code = 400
    assert get_stock_prices(test_date) == {}
