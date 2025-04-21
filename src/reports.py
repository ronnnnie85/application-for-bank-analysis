from datetime import datetime
from typing import Optional

import pandas as pd
from dateutil.relativedelta import relativedelta

from src.config import DATE_TRANSACTIONS_KEY, CATEGORY_KEY, AMOUNT_KEY


def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Функция принимает на вход транзакции, категорию, дату опционально.
    Возвращает траты по данной категории за последние 3 месяца"""
    end_date = datetime.now() if date is None else datetime.strptime(date, "%Y-%m-%d")
    start_date = end_date - relativedelta(months=3)

    transactions[DATE_TRANSACTIONS_KEY] = pd.to_datetime(transactions[DATE_TRANSACTIONS_KEY], dayfirst=True)

    filter_data = (
            (transactions[CATEGORY_KEY] == category) &
            (transactions[DATE_TRANSACTIONS_KEY] >= start_date) &
            (transactions[DATE_TRANSACTIONS_KEY] <= end_date) &
            (transactions[AMOUNT_KEY] < 0)  # Только траты (отрицательные суммы)
    )

    filtered = transactions.loc[filter_data].copy()
    filtered[AMOUNT_KEY] = filtered[AMOUNT_KEY].abs()

    result = filtered.groupby(CATEGORY_KEY).agg({AMOUNT_KEY: 'sum'})

    return result

def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """Функция принимает на вход транзакции, дату опционально.
    Возвращает средние траты в каждый из дней недели за последние три месяца"""
    pass


def spending_by_workday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """Функция принимает на вход транзакции, дату опционально.
    Возвращает средние траты в рабочий и в выходной день за последние три месяца"""
    pass
