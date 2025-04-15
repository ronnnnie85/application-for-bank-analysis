from typing import Optional

import pandas as pd


def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Функция принимает на вход транзакции, категорию, дату опционально.
    Возвращает траты по данной категории за последние 3 месяца"""
    pass


def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """Функция принимает на вход транзакции, дату опционально.
    Возвращает средние траты в каждый из дней недели за последние три месяца"""
    pass


def spending_by_workday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """Функция принимает на вход транзакции, дату опционально.
        Возвращает средние траты в рабочий и в выходной день за последние три месяца"""
    pass