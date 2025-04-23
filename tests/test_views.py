import json
from unittest.mock import patch

from src.config import AMOUNT_ROUND_UP_KEY, CATEGORY_KEY, DATE_TRANSACTIONS_KEY, DESCRIPTION_KEY
from src.views import get_data_events, get_data_main


@patch("src.views.get_stock_prices")
@patch("src.views.get_currency_rates")
@patch("src.views.top_transactions_by_amount")
@patch("src.views.get_total_amount_for_card")
@patch("src.views.get_greetings")
@patch("src.views.read_transactions_from_excel")
def test_get_data_main(
    mock_excel, mock_greetings, mock_amount_card, mock_top, mock_currency, mock_stock, list_transactions
):
    mock_excel.return_value = list_transactions

    mock_greetings.return_value = "Добрый день"

    mock_amount_card.return_value = {"5814": {"sum": 1262.00, "cashback": 12.62}}

    mock_top.return_value = [
        {
            DATE_TRANSACTIONS_KEY: "21.12.2021 20:27:51",
            AMOUNT_ROUND_UP_KEY: 1198.23,
            CATEGORY_KEY: "Переводы",
            DESCRIPTION_KEY: "Перевод Кредитная карта. ТП 10.2 RUR",
        }
    ]

    mock_currency.return_value = {"USD": 73.21}

    mock_stock.return_value = {"AAPL": 150.12}

    result = get_data_main("2018-01-31 12:14:00")
    expected = json.dumps(
        {
            "greeting": "Добрый день",
            "cards": [
                {"last_digits": "5814", "total_spent": 1262.00, "cashback": 12.62},
            ],
            "top_transactions": [
                {
                    "date": "21.12.2021",
                    "amount": 1198.23,
                    "category": "Переводы",
                    "description": "Перевод Кредитная карта. ТП 10.2 RUR",
                },
            ],
            "currency_rates": [{"currency": "USD", "rate": 73.21}],
            "stock_prices": [
                {"stock": "AAPL", "price": 150.12},
            ],
        }
    , indent=4)

    assert result == expected


@patch("src.views.get_stock_prices")
@patch("src.views.get_currency_rates")
@patch("src.views.top_transactions_by_amount")
@patch("src.views.get_total_amount_for_card")
@patch("src.views.get_greetings")
@patch("src.views.read_transactions_from_excel")
def test_get_data_main_err(
    mock_excel, mock_greetings, mock_amount_card, mock_top, mock_currency, mock_stock, list_transactions
):
    mock_excel.return_value = list_transactions

    mock_greetings.return_value = "Добрый день"

    mock_amount_card.return_value = {"5814": {"sum": 1262.00, "cashback": 12.62}}

    mock_top.return_value = [
        {
            DATE_TRANSACTIONS_KEY: "21.12.2021 20:27:51",
            AMOUNT_ROUND_UP_KEY: 1198.23,
            CATEGORY_KEY: "Переводы",
            DESCRIPTION_KEY: "Перевод Кредитная карта. ТП 10.2 RUR",
        }
    ]

    mock_currency.return_value = {"USD": 73.21}

    mock_stock.return_value = {"AAPL": 150.12}

    with patch("src.views.json.dumps") as mock_json:
        mock_json.side_effect = [ValueError, "{}"]
        result = get_data_main("2018-01-31 12:14:00")
    expected = json.dumps({}, indent=4)

    assert result == expected


@patch("src.views.get_stock_prices")
@patch("src.views.get_currency_rates")
@patch("src.views.get_transactions_for_categories")
@patch("src.views.get_amount_for_categories")
@patch("src.views.get_total_amount")
@patch("src.views.read_transactions_from_excel")
def test_get_data_events(
    mock_excel, mock_amount, mock_categories, mock_trans_cat, mock_currency, mock_stock, list_transactions
):
    mock_excel.return_value = list_transactions

    mock_amount.side_effect = [32101, 54271]

    mock_categories.side_effect = [
        {"Супермаркеты": 17319},
        {"Наличные": 500, "Переводы": 200},
        {"Пополнение_BANK007": 33000},
    ]

    mock_currency.return_value = {"USD": 73.21}

    mock_stock.return_value = {"AAPL": 150.12}

    expected = json.dumps(
        {
            "expenses": {
                "total_amount": 32101,
                "main": [
                    {"category": "Супермаркеты", "amount": 17319},
                ],
                "transfers_and_cash": [
                    {"category": "Наличные", "amount": 500},
                    {"category": "Переводы", "amount": 200},
                ],
            },
            "income": {
                "total_amount": 54271,
                "main": [
                    {"category": "Пополнение_BANK007", "amount": 33000},
                ],
            },
            "currency_rates": [
                {"currency": "USD", "rate": 73.21},
            ],
            "stock_prices": [{"stock": "AAPL", "price": 150.12}],
        }
    , indent=4)
    result = get_data_events("2018-01-31 12:14:00")
    assert result == expected


@patch("src.views.get_stock_prices")
@patch("src.views.get_currency_rates")
@patch("src.views.get_transactions_for_categories")
@patch("src.views.get_amount_for_categories")
@patch("src.views.get_total_amount")
@patch("src.views.read_transactions_from_excel")
def test_get_data_events_err(
    mock_excel, mock_amount, mock_categories, mock_trans_cat, mock_currency, mock_stock, list_transactions
):
    mock_excel.return_value = list_transactions

    mock_amount.side_effect = [32101, 54271]

    mock_categories.side_effect = [
        {"Супермаркеты": 17319},
        {"Наличные": 500, "Переводы": 200},
        {"Пополнение_BANK007": 33000},
    ]

    mock_currency.return_value = {"USD": 73.21}

    mock_stock.return_value = {"AAPL": 150.12}

    with patch("src.views.json.dumps") as mock_json:
        mock_json.side_effect = [ValueError, "{}"]
        result = get_data_events("2018-01-31 12:14:00")
    expected = json.dumps({}, indent=4)

    assert result == expected
