import json
from unittest.mock import patch

from src.config import AMOUNT_ROUND_UP_KEY, CATEGORY_KEY, DATE_TRANSACTIONS_KEY, DESCRIPTION_KEY
from src.views import get_data_main


@patch("src.views.get_stock_prices")
@patch("src.views.get_currency_rates")
@patch("src.views.top_transactions_by_amount")
@patch("src.views.get_total_amount_for_card")
@patch("src.views.get_greetings")
@patch("builtins.open")
@patch("src.views.read_transactions_from_excel")
def test_get_data_main(
    mock_excel, mock_file, mock_greetings, mock_amount_card, mock_top, mock_currency, mock_stock, list_transactions
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
    )

    assert result == expected


@patch("src.views.get_stock_prices")
@patch("src.views.get_currency_rates")
@patch("src.views.top_transactions_by_amount")
@patch("src.views.get_total_amount_for_card")
@patch("src.views.get_greetings")
@patch("builtins.open")
@patch("src.views.read_transactions_from_excel")
def test_get_data_main_err(
    mock_excel, mock_file, mock_greetings, mock_amount_card, mock_top, mock_currency, mock_stock, list_transactions
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
    expected = json.dumps({})

    assert result == expected
