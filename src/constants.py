#!/usr/bin/env python3
"""Константы проекта primitive_db."""

from pathlib import Path

# Файл с метаданными БД.
META_FILE = Path("db_meta.json")

# Директория с данными таблиц.
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# Поддерживаемые типы данных.
VALID_TYPES = {"int": int, "str": str, "bool": bool}

# Вспомогательный текст.
HELP_TEXT = """
------------------------------------
***Операции с таблицами и данными***

<command> create_table <имя_таблицы> <столбец:тип> ... - создать таблицу
<command> list_tables - показать список таблиц
<command> drop_table <имя_таблицы> - удалить таблицу

<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...)
- создать запись

<command> select from <имя_таблицы> - прочитать все записи
<command> select from <имя_таблицы> where <столбец> = <значение> 
- прочитать записи по условию

<command> update <имя_таблицы> set <столбец> = <значение> where 
<столбец> = <значение> - обновить записи

<command> delete from <имя_таблицы> where <столбец> = <значение> 
- удалить записи

<command> info <имя_таблицы> - информация о таблице

<command> exit - выход
<command> help - справка
------------------------------------
"""
