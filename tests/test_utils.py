import json
from datetime import datetime
from unittest.mock import mock_open, patch

import pandas as pd
import pytest

from src.utils import (get_amount_for_categories, get_greetings, get_json_file, get_last_digits_card_number,
                       get_start_date, get_total_amount, get_total_amount_for_card, is_valid_datetime,
                       read_df_from_excel, read_transactions_from_excel)


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
    assert get_total_amount_for_card(list_transactions, except_categories={"Переводы", "Супермаркеты"}) == {
        "7197": {"sum": 337.0, "cashback": 6.0}
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
def test_get_start_date(date, period, expected):
    assert get_start_date(date, period) == expected


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
    assert get_amount_for_categories(list_transactions, num_top_cats=1, except_categories={"Супермаркеты"}) == {
        "Переводы": 3000.0,
        "Остальное": 337,
    }


def test_get_amount_for_categories_without_cats(list_transactions_without_cats):
    assert get_amount_for_categories(list_transactions_without_cats) == {
        "Переводы": 3000.0,
        "Супермаркеты": 73.06,
    }


@patch("pandas.read_excel")
def test_transactions_from_xlsx(mock_xlsx, good_df):
    mock_xlsx.return_value = good_df
    assert read_transactions_from_excel("file.csv") == good_df.to_dict("records")


@patch("pandas.read_excel")
def test_read_transactions_from_xlsx_wrong_type(mock_xlsx):
    mock_xlsx.side_effect = ValueError("Тестовая ошибка")
    assert read_transactions_from_excel("file.csv") == []


def test_read_transactions_from_xlsx_file_not_found():
    assert read_transactions_from_excel("") == []


@patch("pandas.read_excel")
def test_read_df_from_excel(mock_xlsx, good_df):
    mock_xlsx.return_value = good_df
    assert read_df_from_excel("file.csv").equals(good_df)


@patch("pandas.read_excel")
def test_read_df_from_excel_wrong_type(mock_xlsx):
    mock_xlsx.side_effect = ValueError("Тестовая ошибка")
    assert read_df_from_excel("file.csv").equals(pd.DataFrame())


def test_read_df_from_excel_file_not_found():
    assert read_df_from_excel("").equals(pd.DataFrame())


def test_is_valid_datetime():
    assert not is_valid_datetime("2012.10.11 15:16:17", "%Y-%m-%d %H:%M:%S")


def test_is_valid_datetime_true():
    assert is_valid_datetime("01.01.2018 20:27:51", "%d.%m.%Y %H:%M:%S")
