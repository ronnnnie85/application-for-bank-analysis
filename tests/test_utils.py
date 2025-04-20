import json
from datetime import datetime
from unittest.mock import mock_open, patch

import pytest

from src.utils import (
    get_amount_for_categories,
    get_cashback_categories,
    get_greetings,
    get_json_file,
    get_last_digits_card_number,
    get_start_date,
    get_total_amount,
    get_total_amount_for_card,
    get_transactions_by_date_period,
    get_transactions_for_categories,
    top_transactions_by_amount,
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
    assert get_total_amount_for_card(list_transactions) == {"7197": {"Сумма": 410.06, "Кэшбек": 7.0}}


@pytest.mark.parametrize(
    "date, period, expected",
    [
        (datetime(2024, 1, 31), "M", datetime(2024, 1, 1)),
        (datetime(2024, 1, 31), "Y", datetime(2024, 1, 1)),
        (datetime(2024, 1, 31), "W", datetime(2024, 1, 29)),
        (datetime(2024, 1, 31), "ALL", datetime(1, 1, 1)),
    ],
)
def test_get_start_date(date, period, expected):
    assert get_start_date(date, period) == expected


def test_get_transactions_by_date_period(list_transactions, tr_by_period):
    assert (
        get_transactions_by_date_period(list_transactions, datetime(2018, 1, 3), datetime(2018, 1, 5)) == tr_by_period
    )


def test_get_transactions_by_date_period_rev(tr_by_period, test_date_start, test_date_end):
    assert get_transactions_by_date_period([{}], test_date_end, test_date_start) == []


def test_top_transactions_by_amount(list_transactions):
    assert top_transactions_by_amount(list_transactions) == [
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
    with patch("src.utils.open", new_callable=mock_open, read_data=test_data):
        assert get_json_file("") == user_settings


def test_get_total_amount(list_transactions):
    assert get_total_amount(list_transactions) == 3410.06


def test_get_total_amount_pos(list_transactions):
    assert get_total_amount(list_transactions, False) == 21.0


def test_get_amount_for_categories(list_transactions):
    assert get_amount_for_categories(list_transactions, num_top_cats=2) == {
        "Переводы": 3000.0,
        "Красота": 337.0,
        "Остальное": 73.06,
    }


def test_get_amount_for_categories_without_cats(list_transactions_without_cats):
    assert get_amount_for_categories(list_transactions_without_cats) == {"Переводы": 3000.0, "Супермаркеты": 73.06}


def test_get_transactions_for_categories(list_transactions):
    assert get_transactions_for_categories(list_transactions, {"Красота", "Переводы"}) == [
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


def test_get_cashback_categories(list_transactions):
    assert get_cashback_categories(list_transactions, percent_cashback=5.0) == {
        "Переводы": 150,
        "Красота": 16,
        "Супермаркеты": 3,
    }
