import json
import logging
import os
import re

from src import loggers
from src.config import AMOUNT_KEY, DATA_FOLDER_NAME, FILE_OPERATIONS
from src.reports import spending_by_category, spending_by_weekday, spending_by_workday
from src.services import (get_beneficial_categories, investment_bank, search_by_phone, search_person_transfer,
                          simple_search)
from src.utils import is_valid_datetime, read_df_from_excel, read_transactions_from_excel
from src.views import get_data_events, get_data_main

name = os.path.splitext(os.path.basename(__file__))[0]
file_name = f"{name}.log"
logger = loggers.create_logger(name, file_name, logging.DEBUG)


def main() -> None:
    """Основная функция для сборки всех компонентов"""

    while True:
        print("Привет! Добро пожаловать в программу анализа банковских операций")
        print("\nВыберите необходимый пункт меню:")
        print('1. Категория "Веб-страницы"')
        print('2. Категория "Сервисы"')
        print('3. Категория "Отчеты"')

        while True:
            choice = input().strip()
            if choice in {"1", "2", "3"}:
                break
            print("Пожалуйста, введите 1, 2 или 3")

        match choice:
            case "1":
                output_pages()
            case "2":
                output_services()
            case "3":
                output_reports()

        exit_answer = input("Продолжить получение информации? y/N\n").strip().lower()
        if exit_answer != "y":
            break


def output_pages() -> None:
    """Функция вывода веб страниц"""
    print('\nКатегория "Веб-страницы"')
    print("1. Главная")
    print("2. События")

    while True:
        choice = input().strip()
        if choice in {"1", "2"}:
            break
        print("Пожалуйста, введите 1, 2")

    while True:
        print("\nВведите дату в формате YYYY-MM-DD HH:MM:SS")
        input_date = input().strip()
        if is_valid_datetime(input_date, "%Y-%m-%d %H:%M:%S"):
            break
        print("Пожалуйста, введите верную дату")

    if choice == "2":
        while True:
            print("\nВведите тип диапазона данных W, M, Y, ALL")
            input_type = input().strip().upper()
            if re.fullmatch(r"^(W|M|Y|ALL)$", input_type):
                break
            if input_type == "":
                input_type = "M"
                break
            else:
                print("Пожалуйста, введите верный диапазон")

        res = get_data_events(input_date, input_type)
    else:
        res = get_data_main(input_date)

    print(res)


def output_services() -> None:
    """Функция вывода сервисов"""
    print('\nКатегория "Сервисы"')
    print("1. Выгодные категории повышенного кешбэка")
    print("2. Инвесткопилка")
    print("3. Простой поиск")
    print("4. Поиск по телефонным номерам")
    print("5. Поиск переводов физическим лицам")

    file_name = os.path.join(os.path.dirname(__file__), f"{DATA_FOLDER_NAME}", FILE_OPERATIONS)
    transactions = read_transactions_from_excel(file_name)
    res: str | float = 0.0
    while True:
        choice = input().strip()
        if choice in {"1", "2", "3", "4", "5"}:
            break
        print("Пожалуйста, введите 1, 2, 3, 4, 5")

    match choice:
        case "1":
            print("\nВведите год месяц процент кэшбека через пробел")
            while True:
                input_data = input().strip()
                if re.fullmatch(r"\d{4}\s+\d{1,2}\s+\d{1,2}(?:\.\d)?", input_data):
                    break
                print("Введите данные верно")

            year, month, percent_cashback = input_data.split(" ")

            res = get_beneficial_categories(transactions, year, month, float(percent_cashback))
        case "2":
            print("\nВведите месяц и лимит округления через пробел")
            while True:
                input_data = input().strip()
                if re.fullmatch(r"^\d{4}-\d{2}\s+(10|50|100)$", input_data):
                    break
                print("Введите данные верно")

            month, limit = input_data.split(" ")

            res = investment_bank(month, transactions, int(limit))
        case "3":
            print("\nВведите ключевое слово")
            while True:
                input_data = input().strip()
                if re.fullmatch(r"\b[\w'-]+\b", input_data):
                    break
                print("Введите данные верно")

            res = simple_search(transactions, input_data)
        case "4":
            res = search_by_phone(transactions)
        case "5":
            res = search_person_transfer(transactions)

    print(res)


def output_reports() -> None:
    """Функция вывода отчетов"""
    print('\nКатегория "Отчеты"')
    print("1. Траты по категории")
    print("2. Траты по дням недели")
    print("3. Траты в рабочий/выходной день")

    file_name = os.path.join(os.path.dirname(__file__), f"{DATA_FOLDER_NAME}", FILE_OPERATIONS)
    transactions = read_df_from_excel(file_name)

    while True:
        choice = input().strip()
        if choice in {"1", "2", "3"}:
            break
        print("Пожалуйста, введите 1, 2, 3")

    match choice:
        case "1":
            print("\nВведите категорию и опционально дату в формате YYYY-MM-DD через пробел")
            while True:
                input_data = input().strip()
                if re.fullmatch(r"^\w+(?:\s+\d{4}-\d{2}-\d{2})?$", input_data):
                    break
                print("Введите данные верно")

            lst = input_data.split(" ")

            if len(lst) == 2:
                category, date = lst
            else:
                category = lst[0]
                date = None
            res = spending_by_category(transactions, category, date)
        case "2":
            print("\nВведите опционально дату в формате YYYY-MM-DD через пробел")
            while True:
                input_data = input().strip()
                if input_data:
                    if is_valid_datetime(input_data, "%Y-%m-%d"):
                        data = input_data
                        break
                    print("Введите данные верно")
                else:
                    data = None
                    break

            res = spending_by_weekday(transactions, data)
        case "3":
            print("\nВведите опционально дату в формате YYYY-MM-DD через пробел")
            while True:
                input_data = input().strip()
                if input_data:
                    if is_valid_datetime(input_data, "%Y-%m-%d"):
                        data = input_data
                        break
                    print("Введите данные верно")
                else:
                    data = None
                    break

            res = spending_by_workday(transactions, data)

    json_data = res[AMOUNT_KEY].to_dict()
    print(json.dumps(json_data, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()
