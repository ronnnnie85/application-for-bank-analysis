from typing import Any


def get_beneficial_categories(data: list[dict[str, Any]], year: str, month: str, percent_cashback: float = 5.0) -> str:
    """На вход функции поступают данные для анализа, год и месяц. На выходе — JSON с анализом,
    сколько на каждой категории можно заработать кешбэка в указанном месяце года."""
    pass


def investment_bank(month: str, transactions: list[dict[str, Any]], limit: int) -> float:
    """На вход функции поступают месяц и список транзакций. На выходе возможная сумма в инвесткопилку"""
    pass


def simple_search(transactions: list[dict[str, Any]], keyword: str) -> str:
    """На вход функции поступает список транзакция и ключевое слова.
    На выходе JSON-ответ со всеми транзакциями, содержащими запрос в описании или категории."""
    pass


def search_by_phone(transactions: list[dict[str, Any]]) -> str:
    """Функция возвращает JSON со всеми транзакциями, содержащими в описании мобильные номера."""
    pass


def search_person_transfer(transactions: list[dict[str, Any]]) -> str:
    """Функция возвращает JSON со всеми транзакциями, которые относятся к переводам физлицам.
    Категория такой транзакции — Переводы, а в описании есть имя и первая буква фамилии с точкой."""
    pass
