#!/usr/bin/env python3
"""Игровой цикл: парсинг команд и запуск функций."""

import shlex
import prompt
from pathlib import Path
from prettytable import PrettyTable

from .utils import (
    load_metadata,
    save_metadata,
    load_table_data,
    save_table_data,
)
from .core import (
    create_table,
    drop_table,
    list_tables,
    insert,
    select,
    update,
    delete,
    info,
)

DB_META_FILE = Path("db_meta.json")

HELP_TEXT = """
***Операции с таблицами и данными***

<command> create_table <имя_таблицы> <столбец:тип> ... - создать таблицу
<command> list_tables - показать список таблиц
<command> drop_table <имя_таблицы> - удалить таблицу

<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) - создать запись
<command> select from <имя_таблицы> - прочитать все записи
<command> select from <имя_таблицы> where <столбец> = <значение> - прочитать записи по условию
<command> update <имя_таблицы> set <столбец> = <значение> where <столбец> = <значение> - обновить записи
<command> delete from <имя_таблицы> where <столбец> = <значение> - удалить записи
<command> info <имя_таблицы> - информация о таблице

<command> exit - выход
<command> help - справка
"""


def print_help() -> None:
    """Печатает список доступных команд."""
    print(HELP_TEXT)


# ---------- Парсеры условий ----------

def parse_where(tokens: list[str]) -> dict:
    """Парсит условие WHERE в формате col = value."""
    if len(tokens) < 3 or tokens[1] != "=":
        print("Некорректный синтаксис WHERE.")
        return {}
    col, _, val = tokens
    if val.startswith('"') and val.endswith('"'):
        val = val.strip('"')
    return {col: val}


def parse_set(tokens: list[str]) -> dict:
    """Парсит условие SET в формате col = value."""
    if len(tokens) < 3 or tokens[1] != "=":
        print("Некорректный синтаксис SET.")
        return {}
    col, _, val = tokens
    if val.startswith('"') and val.endswith('"'):
        val = val.strip('"')
    return {col: val}


# ---------- Основной цикл ----------

def run() -> None:
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

        if not args:
            continue

        command = args[0]

        # ----- Таблицы -----
        if command == "create_table":
            if len(args) < 2:
                print("Укажите имя таблицы и хотя бы один столбец.")
                continue
            metadata = create_table(metadata, args[1], args[2:])
            save_metadata(DB_META_FILE, metadata)

        elif command == "drop_table":
            if len(args) < 2:
                print("Укажите имя таблицы.")
                continue
            metadata = drop_table(metadata, args[1])
            save_metadata(DB_META_FILE, metadata)

        elif command == "list_tables":
            list_tables(metadata)

        # ----- CRUD -----
        elif command == "insert":
            # insert into users values ("Sergei", 28, true)
            if len(args) < 4 or args[1] != "into" or args[3] != "values":
                print("Синтаксис: insert into <table> values (...)")
                continue
            table_name = args[2]
            values_str = user_input.split("values", 1)[1].strip()
            if values_str.startswith("(") and values_str.endswith(")"):
                values_str = values_str[1:-1]
            raw_values = [v.strip() for v in values_str.split(",")]
            # Убираем кавычки вокруг строк
            values = []
            for v in raw_values:
                if v.startswith('"') and v.endswith('"'):
                    values.append(v.strip('"'))
                elif v.lower() in ("true", "false"):
                    values.append(v.lower() == "true")
                else:
                    try:
                        values.append(int(v))
                    except ValueError:
                        values.append(v)

            data = load_table_data(table_name)
            data = insert(metadata, table_name, values, data)
            save_table_data(table_name, data)

        elif command == "select":
            # select from users [where age = 28]
            if len(args) < 3 or args[1] != "from":
                print("Синтаксис: select from <table> [where ...]")
                continue
            table_name = args[2]
            data = load_table_data(table_name)

            where_clause = None
            if len(args) > 3 and args[3] == "where":
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
            if len(args) < 5 or args[2] != "set":
                print(
                    "Синтаксис: update <table> "
                    "set <col>=<val> where <col>=<val>"
                )
                continue
            table_name = args[1]
            if "where" not in args:
                print("Отсутствует условие WHERE.")
                continue
            where_index = args.index("where")
            set_clause = parse_set(args[3:where_index])
            where_clause = parse_where(args[where_index + 1:])
            data = load_table_data(table_name)
            data = update(data, set_clause, where_clause)
            save_table_data(table_name, data)

        elif command == "delete":
            # delete from users where ID = 1
            if len(args) < 4 or args[1] != "from" or args[3] != "where":
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

        # ----- Служебные -----
        elif command == "help":
            print_help()

        elif command == "exit":
            break

        else:
            print(f"Функции {command} нет. Попробуйте снова.")
