from datetime import datetime

import pytest

from src.utils import get_greetings


@pytest.mark.parametrize("date, expected", [(datetime(2025, 4, 15, 1), "Доброй ночи"),
                                            (datetime(2025, 4, 15, 6), "Доброе утро"),
                                            (datetime(2025, 4, 15, 17, 59, 59), "Добрый день"),
                                            (datetime(2025, 4, 15, 19), "Добрый вечер")])
def test_get_greetings(date, expected):
    assert get_greetings(date) == expected