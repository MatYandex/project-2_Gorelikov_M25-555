#!/usr/bin/env python3

import shlex
from pathlib import Path

import prompt

from .utils import load_metadata, save_metadata
from .core import create_table, drop_table, list_tables

DB_META_FILE = Path("db_meta.json")
HELP_TEXT = """
***Процесс работы с таблицей***
<command> create_table <имя_таблицы> <столбец:тип> ... - создать таблицу
<command> list_tables - показать список таблиц
<command> drop_table <имя_таблицы> - удалить таблицу
<command> exit - выход
<command> help - справка
"""


def print_help() -> None:
    """Печатает список доступных команд."""
    print(HELP_TEXT)


def run():
    """Основной цикл программы."""
    print_help()
    while True:
        metadata = load_metadata(DB_META_FILE)
        user_input = prompt.string("Введите команду: ")

        try:
            args = shlex.split(user_input)
        except ValueError:
            print("Ошибка разбора команды. Попробуйте снова.")
            continue

        command, *params = args

        if command == "create_table":
            if not params:
                print("Укажите имя таблицы и столбцы.")
                continue
            metadata = create_table(metadata, params[0], params[1:])
            save_metadata(DB_META_FILE, metadata)

        elif command == "drop_table":
            if not params:
                print("Укажите имя таблицы.")
                continue
            metadata = drop_table(metadata, params[0])
            save_metadata(DB_META_FILE, metadata)

        elif command == "list_tables":
            list_tables(metadata)

        elif command == "help":
            print_help()

        elif command == "exit":
            break

        else:
            print(f"Функции {command} нет. Попробуйте снова.")
