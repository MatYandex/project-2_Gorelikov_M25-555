#!/usr/bin/env python3
"""Игровой цикл"""

import shlex

import prompt
from prettytable import PrettyTable

from src.constants import HELP_TEXT, META_FILE

from .core import (
    create_table,
    delete,
    drop_table,
    info,
    insert,
    list_tables,
    select,
    update,
)
from .parser import parse_insert, parse_set_where
from .utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def print_help() -> None:
    """Печатает список доступных команд."""
    print(HELP_TEXT)


def check_args(args: list[str], min_len: int, command_name: str) -> bool:
    """Проверяет минимальное количество аргументов для команды."""
    if len(args) < min_len:
        print(f"Укажите аргументы для команды {command_name}.")
        return False
    return True


def find_keyword_index(args: list[str], keyword: str) -> int:
    """Возвращает индекс ключевого слова в args или -1, если не найдено."""
    keyword_lower = keyword.lower()
    for i, arg in enumerate(args):
        if arg.lower() == keyword_lower:
            return i
    return -1


def run() -> None:
    """Основной цикл программы."""
    print_help()

    while True:
        metadata = load_metadata(META_FILE)
        try:
            user_input = prompt.string("Введите команду: ")
        except Exception as e:
            print(f"Ошибка ввода: {e}")
            continue

        try:
            args = shlex.split(user_input)
        except ValueError:
            print("Ошибка разбора команды. Попробуйте снова.")
            continue

        if not args:
            continue

        args_lower = [a.lower() for a in args]
        command = args_lower[0]

        try:
            if command == "create_table":
                if not check_args(args, 2, "create_table"):
                    continue
                metadata = create_table(metadata, args[1], args[2:])
                save_metadata(META_FILE, metadata)

            elif command == "drop_table":
                if not check_args(args, 2, "drop_table"):
                    continue
                result = drop_table(metadata, args[1])
                if result is not None:
                    metadata = result
                    save_metadata(META_FILE, metadata)

            elif command == "list_tables":
                list_tables(metadata)

            elif command == "insert":
                if (
                        len(args) < 4
                        or args_lower[1] != "into"
                        or args_lower[3] != "values"
                ):
                    print("Синтаксис: insert into <table> values (...)")
                    continue

                table_name = args[2]
                values_index = user_input.lower().find("values")
                values_str = user_input[values_index + len("values"):]
                values = parse_insert(values_str)

                data = load_table_data(table_name)
                data = insert(metadata, table_name, values, data)
                save_table_data(table_name, data)

            elif command == "select":
                if len(args) < 3 or args_lower[1] != "from":
                    print("Синтаксис: select from <table> [where ...]")
                    continue

                table_name = args[2]
                data = load_table_data(table_name)

                where_clause = None
                if len(args) > 3 and args_lower[3] == "where":
                    where_clause = parse_set_where(args[4:])

                rows = select(data, where_clause)
                if not rows:
                    print("Нет данных.")
                    continue

                table = PrettyTable()
                table.field_names = rows[0].keys()
                for row in rows:
                    table.add_row(row.values())
                print(table)

            elif command == "update":
                if len(args) < 5 or args_lower[2] != "set":
                    print(
                        "Синтаксис: update <table> set <col>=<val> "
                        "where <col>=<val>"
                    )
                    continue

                table_name = args[1]
                where_index = find_keyword_index(args, "where")
                if where_index == -1:
                    print("Отсутствует условие WHERE.")
                    continue

                set_clause = parse_set_where(args[3:where_index])
                where_clause = parse_set_where(args[where_index + 1:])
                data = load_table_data(table_name)
                data = update(data, set_clause, where_clause)
                save_table_data(table_name, data)

            elif command == "delete":
                if (
                        len(args) < 4
                        or args_lower[1] != "from"
                        or args_lower[3] != "where"
                ):
                    print(
                        "Синтаксис: delete from <table> "
                        "where <col>=<val>"
                    )
                    continue

                table_name = args[2]
                where_clause = parse_set_where(args[4:])
                data = load_table_data(table_name)
                result = delete(data, where_clause)
                if result is not None:
                    save_table_data(table_name, result)

            elif command == "info":
                if not check_args(args, 2, "info"):
                    continue
                table_name = args[1]
                data = load_table_data(table_name)
                info(metadata, table_name, data)

            elif command == "help":
                print_help()

            elif command == "exit":
                break

            else:
                print(f"Функции {command} нет. Попробуйте снова.")

        except Exception as e:
            print(f"Произошла ошибка: {e}")
            continue
