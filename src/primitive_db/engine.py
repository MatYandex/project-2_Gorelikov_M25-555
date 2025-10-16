#!/usr/bin/env python3
"""Игровой цикл: парсинг команд и запуск функций."""

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
from .parser import parse_set, parse_where
from .utils import load_metadata, load_table_data, save_metadata, save_table_data


def print_help() -> None:
    """Печатает список доступных команд."""
    print(HELP_TEXT)


def run() -> None:
    """Основной цикл программы."""
    print_help()

    while True:
        metadata = load_metadata(META_FILE)
        user_input = prompt.string("Введите команду: ")

        try:
            args = shlex.split(user_input)
        except ValueError:
            print("Ошибка разбора команды. Попробуйте снова.")
            continue

        if not args:
            continue

        command = args[0].lower()

        try:
            if command == "create_table":
                if len(args) < 2:
                    print("Укажите имя таблицы и хотя бы один столбец.")
                    continue
                metadata = create_table(metadata, args[1], args[2:])
                save_metadata(META_FILE, metadata)

            elif command == "drop_table":
                if len(args) < 2:
                    print("Укажите имя таблицы.")
                    continue
                metadata = drop_table(metadata, args[1])
                if metadata is not None:
                    save_metadata(META_FILE, metadata)

            elif command == "list_tables":
                list_tables(metadata)

            elif command == "insert":
                # insert into users values ("Sergei, Jr.", 28, true)
                if len(args) < 4 or args[1].lower() != "into" or (
                        args[3].lower() != "values"):
                    print("Синтаксис: insert into <table> values (...)")
                    continue
                table_name = args[2]
                values_index = user_input.lower().find("values")
                values_str = user_input[values_index + len("values"):].strip()
                if values_str.startswith("(") and values_str.endswith(")"):
                    values_str = values_str[1:-1]

                raw_values = shlex.split(values_str)
                values = [tok.rstrip(',') for tok in raw_values if tok != ","]

                data = load_table_data(table_name)
                data = insert(metadata, table_name, values, data)
                save_table_data(table_name, data)

            elif command == "select":
                # select from users [where age = 28]
                if len(args) < 3 or args[1].lower() != "from":
                    print("Синтаксис: select from <table> [where ...]")
                    continue
                table_name = args[2]
                data = load_table_data(table_name)

                where_clause = None
                if len(args) > 3 and args[3].lower() == "where":
                    where_clause = parse_where(args[4:])

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
                # update users set age = 29 where name = "Sergei"
                if len(args) < 5 or args[2].lower() != "set":
                    print("Синтаксис: update <table>"
                          " set <col>=<val> where <col>=<val>")
                    continue
                table_name = args[1]
                if "where" not in [x.lower() for x in args]:
                    print("Отсутствует условие WHERE.")
                    continue
                where_index = next(
                    i for i, x in enumerate(args) if x.lower() == "where")
                set_clause = parse_set(args[3:where_index])
                where_clause = parse_where(args[where_index + 1:])
                data = load_table_data(table_name)
                data = update(data, set_clause, where_clause)
                save_table_data(table_name, data)

            elif command == "delete":
                # delete from users where ID = 1
                if len(args) < 4 or args[1].lower() != "from" or (
                        args[3].lower() != "where"):
                    print("Синтаксис: delete from <table> where <col>=<val>")
                    continue
                table_name = args[2]
                where_clause = parse_where(args[4:])
                data = load_table_data(table_name)
                data = delete(data, where_clause)
                save_table_data(table_name, data)

            elif command == "info":
                if len(args) < 2:
                    print("Укажите имя таблицы.")
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

        except Exception:
            # Ошибки обработаны в core.py и decorators.py.
            continue
