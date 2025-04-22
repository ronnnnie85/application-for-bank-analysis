import logging
import os
from datetime import datetime
from typing import Optional

import pandas as pd
from dateutil.relativedelta import relativedelta

from src import loggers
from src.config import AMOUNT_KEY, CATEGORY_KEY, DATE_TRANSACTIONS_KEY

name = os.path.splitext(os.path.basename(__file__))[0]
file_name = f"{name}.log"
logger = loggers.create_logger(name, file_name, logging.DEBUG)


def get_dataframe_spending(
    df: pd.DataFrame,
    start_date: datetime,
    end_date: datetime,
    category: str = "",
    expense: bool = True,
) -> pd.DataFrame:
    """Принимает на вход dataframe, начальную и конечную даты, опционально категорию и признак расходов.
    Возвращает фильтрованый dataframe"""
    df[DATE_TRANSACTIONS_KEY] = pd.to_datetime(df[DATE_TRANSACTIONS_KEY], dayfirst=True)

    filter_data = (df[DATE_TRANSACTIONS_KEY] >= start_date) & (df[DATE_TRANSACTIONS_KEY] <= end_date)

    if category:
        filter_data &= df[CATEGORY_KEY] == category

    if expense:
        filter_data &= df[AMOUNT_KEY] < 0
    else:
        filter_data &= df[AMOUNT_KEY] > 0

    filtered = df.loc[filter_data].copy()
    filtered[AMOUNT_KEY] = filtered[AMOUNT_KEY].abs()
    # filtered[DATE_TRANSACTIONS_KEY] = filtered[DATE_TRANSACTIONS_KEY].dt.strftime("%d.%m.%Y %H:%M:%S")
    logger.info("Получены фильтрованные dataframe")
    return filtered


def get_dates_by_month(date: Optional[str], months: int = 3) -> tuple[datetime, datetime]:
    """Принимает строковую дату, возвращает дату начала конца в datetime"""
    end_date = datetime.now() if date is None else datetime.strptime(date, "%Y-%m-%d")
    start_date = end_date - relativedelta(months=months)
    logger.info("Получены даты")
    return start_date, end_date
