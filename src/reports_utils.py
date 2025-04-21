from datetime import datetime
from typing import Optional

import pandas as pd
from dateutil.relativedelta import relativedelta

from src.config import DATE_TRANSACTIONS_KEY, CATEGORY_KEY, AMOUNT_KEY


def get_dataframe_spending(
    df: pd.DataFrame, start_date: datetime, end_date: datetime, category: str = "", expense: bool = True
) -> pd.DataFrame:
    """Принимает на вход dataframe, начальную и конечную даты, опционально категорию и признак расходов.
    Возвращает фильтрованый список"""
    df[DATE_TRANSACTIONS_KEY] = pd.to_datetime(df[DATE_TRANSACTIONS_KEY], dayfirst=True)

    filter_data = (
        (df[CATEGORY_KEY] == category if category else True)
        & (df[DATE_TRANSACTIONS_KEY] >= start_date)
        & (df[DATE_TRANSACTIONS_KEY] <= end_date)
        & (df[AMOUNT_KEY] < 0 if expense else df[AMOUNT_KEY] > 0)
    )

    filtered = df.loc[filter_data].copy()
    filtered[AMOUNT_KEY] = filtered[AMOUNT_KEY].abs()

    return filtered


def get_dates_by_month(date: Optional[str], months: int = 3) -> tuple[datetime, datetime]:
    """Принимает строковую дату, возвращает дату начала конца в datetime"""
    end_date = datetime.now() if date is None else datetime.strptime(date, "%Y-%m-%d")
    start_date = end_date - relativedelta(months=months)

    return start_date, end_date