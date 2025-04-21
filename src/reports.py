import functools
import json
import os
from datetime import datetime
from typing import Optional

import pandas as pd
from dateutil.relativedelta import relativedelta

from src.config import DATE_TRANSACTIONS_KEY, CATEGORY_KEY, AMOUNT_KEY, REPORTS_FOLDER_NAME, RUSSIAN_DAYS
from src.utils import get_dataframe_spending, get_dates_by_month


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
    start_date, end_date = get_dates_by_month(date)

    filtered = get_dataframe_spending(transactions, start_date, end_date, category=category)
    result = filtered.groupby(CATEGORY_KEY).agg({AMOUNT_KEY: "sum"}).round(2)

    return result


@log_reports_to_file("spending_by_weekday.json")
def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """Функция принимает на вход транзакции, дату опционально.
    Возвращает средние траты в каждый из дней недели за последние три месяца"""
    start_date, end_date = get_dates_by_month(date)

    filtered = get_dataframe_spending(transactions, start_date, end_date)
    filtered["day_of_week"] = filtered[DATE_TRANSACTIONS_KEY].dt.weekday
    filtered["day_name_ru"] = filtered["day_of_week"].map((lambda x: RUSSIAN_DAYS[x]))
    result = filtered.groupby("day_name_ru").agg({AMOUNT_KEY: "sum", "day_of_week": "first"}).round(2)
    result = result.sort_values("day_of_week")

    return result


@log_reports_to_file("spending_by_workday.json")
def spending_by_workday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """Функция принимает на вход транзакции, дату опционально.
    Возвращает средние траты в рабочий и в выходной день за последние три месяца"""
    start_date, end_date = get_dates_by_month(date)

    filtered = get_dataframe_spending(transactions, start_date, end_date)



spending_by_weekday(pd.read_excel("../data/operations.xlsx"), "2021-06-01")
