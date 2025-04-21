from src.services_utils import get_cashback_categories, get_invest_amount, get_search_by_keyword


def test_get_cashback_categories(list_transactions):
    assert get_cashback_categories(list_transactions, percent_cashback=5.0) == {
        "Переводы": 150,
        "Красота": 16,
        "Супермаркеты": 3,
    }


def test_get_invest_amount(tr_by_period):
    assert get_invest_amount(tr_by_period, 50) == 55.94


def test_get_search_by_keyword(list_transactions):
    assert get_search_by_keyword(list_transactions, "перевод", {"Категория"}) == [
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
