#!/usr/bin/env python3
"""Вспомогательные функции для работы с метаданными БД."""

import json


def load_metadata(filepath: str) -> dict:
    """
    Загружает метаданные из JSON файла.
    Если файл не найден, возвращает пустой словарь.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_metadata(filepath: str, data: dict) -> None:
    """
    Сохраняет метаданные в JSON файл.
    """
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
