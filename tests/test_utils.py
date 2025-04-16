from datetime import datetime

import pytest

from src.utils import get_greetings, get_last_digits_card_number, get_total_amount, get_start_data


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


def test_get_total_amount(list_transactions):
    assert get_total_amount(list_transactions, "2018-01-30 14:30:56", "M") == {"7197": {"Сумма": 410.06, "Кэшбек": 7.0}}


@pytest.mark.parametrize("date, period, expected", [(datetime(2024, 1, 31), "M", datetime(2024, 1, 1)),
                                            (datetime(2024, 1, 31), "Y", datetime(2024, 1, 1)),
                                            (datetime(2024, 1, 31), "W", datetime(2024, 1, 29)),
                                            (datetime(2024, 1, 31), "ALL", datetime(1, 1, 1))])
def test_get_start_data(date, period, expected):
    assert get_start_data(date, period) == expected
