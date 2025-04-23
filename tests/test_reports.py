from unittest.mock import patch

import pandas as pd

from src.reports import log_reports_to_file, spending_by_category, spending_by_weekday, spending_by_workday


@patch("src.reports.json.dump")
@patch("builtins.open")
def test_log_reports_to_file(mock_file, mock_json, df_test):
    @log_reports_to_file("test.json")
    def foo():
        return df_test

    assert foo().equals(df_test)
    mock_file.assert_called_once()
    mock_json.assert_called_once()


@patch("builtins.open")
def test_log_reports_to_file_err(mock_file, df_test):
    @log_reports_to_file("test.json")
    def foo():
        return df_test

    mock_file.side_effect = FileNotFoundError
    assert foo().equals(df_test)
    mock_file.assert_called_once()


def test_spending_by_category(df_test):
    result_df = spending_by_category(df_test, "Красота", "2018-02-01")
    data = [{"Категория": "Красота", "Сумма операции": 337.0}]
    df = pd.DataFrame(data).set_index("Категория")
    expected_df = pd.DataFrame(df)
    assert result_df.equals(expected_df)


def test_spending_by_weekday(df_test):
    result_df = spending_by_weekday(df_test, "2018-02-01")

    data = {"Сумма операции": [3316.00, 94.06], "day_of_week": [0, 2]}
    expected_df = pd.DataFrame(data, index=["Понедельник", "Среда"])
    expected_df.index.name = "day_name_ru"

    pd.testing.assert_frame_equal(result_df, expected_df, check_dtype=False)


def test_spending_by_workday(df_test):
    result_df = spending_by_workday(df_test, "2018-02-01")

    data = {"Сумма операции": [3410.06]}
    expected_df = pd.DataFrame(data, index=["Рабочий день"])
    expected_df.index.name = "type_day"

    pd.testing.assert_frame_equal(result_df, expected_df, check_dtype=False)  # Игнорируем различия типов
