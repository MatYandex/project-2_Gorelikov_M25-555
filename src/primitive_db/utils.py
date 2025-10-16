#!/usr/bin/env python3
"""Вспомогательные функции для работы с метаданными и таблицами."""

import json

from src.constants import DATA_DIR

DATA_DIR.mkdir(exist_ok=True)


def load_metadata(filepath: str) -> dict:
    """Загружает метаданные из JSON файла."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_metadata(filepath: str, data: dict) -> None:
    """Сохраняет метаданные в JSON файл."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_table_data(table_name: str) -> list[dict]:
    """
    Загружает данные таблицы из файла data/<table>.json.
    Если файла нет, возвращает пустой список.
    """
    table_file = DATA_DIR / f"{table_name}.json"
    try:
        with open(table_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_table_data(table_name: str, data: list[dict]) -> None:
    """Сохраняет данные таблицы в файл data/<table>.json."""
    table_file = DATA_DIR / f"{table_name}.json"
    with open(table_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
