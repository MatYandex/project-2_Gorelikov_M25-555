#!/usr/bin/env python3
"""Парсеры сложных функций."""


def parse_where(tokens: list[str]) -> dict:
    """Парсит условие WHERE в формате col = value."""
    if len(tokens) < 3 or tokens[1] != "=":
        print("Некорректный синтаксис WHERE.")
        return {}
    col, _, val = tokens
    val = val.strip('"') if val.startswith('"') and val.endswith('"') else val
    return {col: val}


def parse_set(tokens: list[str]) -> dict:
    """Парсит условие SET в формате col = value."""
    if len(tokens) < 3 or tokens[1] != "=":
        print("Некорректный синтаксис SET.")
        return {}
    col, _, val = tokens
    val = val.strip('"') if val.startswith('"') and val.endswith('"') else val
    return {col: val}
