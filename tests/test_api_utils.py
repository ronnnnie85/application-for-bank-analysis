from unittest.mock import patch

import requests

from src.api_utils import get_currency_rates, get_stock_prices


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
