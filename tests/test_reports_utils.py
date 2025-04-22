from datetime import datetime

from src.reports_utils import get_dataframe_spending, get_dates_by_month


def test_get_dataframe_spending(dataframe_tr, test_date_start, test_date_end):
    result_df = get_dataframe_spending(dataframe_tr, test_date_start, test_date_end, "Красота")

    result_records = result_df.copy()
    result_records['Дата операции'] = result_records['Дата операции'].dt.strftime('%d.%m.%Y %H:%M:%S')
    result_records = result_records.to_dict('records')

    expected = [
        {
            "Дата операции": "01.01.2018 20:27:51",
            "Дата платежа": "04.01.2018",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма операции": 316.0,
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
            "Дата операции": "03.01.2018 14:55:21",
            "Дата платежа": "05.01.2018",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма операции": 21.0,
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
    ]

    assert result_records == expected


def test_get_dataframe_spending_incomes(dataframe_tr, test_date_start, test_date_end):
    result_df = get_dataframe_spending(dataframe_tr, test_date_start, test_date_end, "Красота", False)

    result_records = result_df.copy()
    result_records['Дата операции'] = result_records['Дата операции'].dt.strftime('%d.%m.%Y %H:%M:%S')
    result_records = result_records.to_dict('records')

    expected = [
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
        }
    ]

    assert result_records == expected


def test_get_dates_by_month():
    assert get_dates_by_month("2019-01-01") == (datetime(2018, 10, 1), datetime(2019, 1, 1))
