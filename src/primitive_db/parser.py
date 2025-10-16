#!/usr/bin/env python3
"""Парсеры сложных функций."""

import shlex


def parse_set_where(tokens: list[str]) -> dict:
    """
    Парсит условие SET/WHERE
    в формате col = value.
    """
    if len(tokens) < 3 or tokens[1] != "=":
        print("Некорректный синтаксис SET.")
        return {}
    col, _, val = tokens
    val = val.strip('"') if val.startswith('"') and val.endswith('"') else val
    return {col: val}


def parse_insert(values_str: str) -> list:
    """
    Разбирает строку вида '(value1, value2, ...)'
    и возвращает список значений.
    Учтены кавычки для строк с пробелами и запятыми.
    """
    values_str = values_str.strip()
    if values_str.startswith("(") and values_str.endswith(")"):
        values_str = values_str[1:-1]

    # shlex.split учитывает кавычки
    raw_values = shlex.split(values_str)
    # убираем лишние запятые, которые могли остаться после split
    values = [tok.rstrip(',') for tok in raw_values if tok != ","]
    return values
