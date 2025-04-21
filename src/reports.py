import functools
import json
import os
from datetime import datetime
from typing import Optional

import pandas as pd
from dateutil.relativedelta import relativedelta

from src.config import DATE_TRANSACTIONS_KEY, CATEGORY_KEY, AMOUNT_KEY, REPORTS_FOLDER_NAME


def log_reports_to_file(file_name: str = "report.json"):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            df = func(*args, **kwargs)
            dct = df[AMOUNT_KEY].to_dict()

            file_path = os.path.join(os.path.dirname(__file__), f"../{REPORTS_FOLDER_NAME}", file_name)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(dct, f, ensure_ascii=False, indent=4)

            return df
        return wrapper
    return decorator


@log_reports_to_file("spending_by_category.json")
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


spending_by_category(pd.read_excel("../data/operations.xlsx"), "Переводы", "2021-06-01")