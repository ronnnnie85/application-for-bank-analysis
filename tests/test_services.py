import json
from unittest.mock import patch

from src.services import (
    get_beneficial_categories,
    investment_bank,
    simple_search,
    search_by_phone,
    search_person_transfer,
)


def test_get_beneficial_categories(list_transactions):
    res_json = get_beneficial_categories(list_transactions, "2018", "01")
    assert json.loads(res_json) == {"Красота": 16.0, "Супермаркеты": 3.0}


@patch("src.services.json.dumps")
def test_get_beneficial_categories_err(mock_json, list_transactions):
    mock_json.side_effect = [ValueError, "{}"]
    res_json = get_beneficial_categories(list_transactions, "2018", "01")
    assert json.loads(res_json) == {}


def test_investment_bank(list_transactions):
    assert investment_bank("2018-01", list_transactions, 50) == 89.94


def test_simple_search(list_transactions):
    res_json = simple_search(list_transactions, "Линзомат")
    assert json.loads(res_json) == [
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
        }
    ]


@patch("src.services.json.dumps")
def test_simple_search_err(mock_json, list_transactions):
    mock_json.side_effect = [ValueError, "{}"]
    res_json = simple_search(list_transactions, "Линзомат")
    assert json.loads(res_json) == {}


def test_search_by_phone(list_tr):
    res_json = search_by_phone(list_tr)
    assert json.loads(res_json) == [
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
            "Описание": "Я МТС +7 921 211-22-33",
            "Бонусы (включая кэшбэк)": 6,
            "Округление на инвесткопилку": 0,
            "Сумма операции с округлением": 316.0,
        }
    ]


@patch("src.services.json.dumps")
def test_search_by_phone_err(mock_json, list_tr):
    mock_json.side_effect = [ValueError, "{}"]
    res_json = search_by_phone(list_tr)
    assert json.loads(res_json) == {}


def test_search_person_transfer(list_tr):
    res_json = search_person_transfer(list_tr)
    assert json.loads(res_json) == [
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
            "Описание": "Иван С.",
            "Бонусы (включая кэшбэк)": 0,
            "Округление на инвесткопилку": 0,
            "Сумма операции с округлением": 3000.0,
        }
    ]


@patch("src.services.json.dumps")
def test_search_person_transfer_err(mock_json, list_tr):
    mock_json.side_effect = [ValueError, "{}"]
    res_json = search_person_transfer(list_tr)
    assert json.loads(res_json) == {}
