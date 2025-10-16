#!/usr/bin/env python3
"""Основная логика управления таблицами и CRUD с декораторами."""

from src.constants import VALID_TYPES
from src.decorators import confirm_action, create_cacher, handle_db_errors, log_time

cache_result = create_cacher()


def normalize_value(value):
    """Приводит значение к единому виду для корректного сравнения."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        low = value.lower()
        if low in ("true", "1"):
            return True
        if low in ("false", "0"):
            return False
        # Числа
        if value.isdigit():
            return int(value)
    return value


@handle_db_errors
def create_table(metadata: dict, table_name: str, columns: list[str]) -> dict:
    """Создаёт таблицу с указанными столбцами."""
    if table_name in metadata:
        raise KeyError(table_name)

    table_columns = [("ID", "int")]
    for col in columns:
        if ":" not in col:
            raise ValueError(f"Некорректный формат столбца: {col}")
        name, col_type = col.split(":")
        if col_type not in VALID_TYPES:
            raise ValueError(
                f"Некорректный тип: {col_type}. "
                f"Допустимые: {', '.join(VALID_TYPES)}"
            )
        table_columns.append((name, col_type))

    metadata[table_name] = table_columns
    print(
        f'Таблица "{table_name}" успешно создана со столбцами: '
        + ", ".join(f"{n}:{t}" for n, t in table_columns)
    )
    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata: dict, table_name: str) -> dict:
    """Удаляет таблицу и её данные, если она существует."""
    import os

    from src.constants import DATA_DIR

    if table_name not in metadata:
        raise KeyError(table_name)

    del metadata[table_name]

    table_file = DATA_DIR / f"{table_name}.json"
    if table_file.exists():
        os.remove(table_file)

    cache_result.invalidate()

    print(f'Таблица "{table_name}" и её данные успешно удалены.')
    return metadata


@handle_db_errors
def list_tables(metadata: dict) -> None:
    """Выводит список таблиц."""
    if not metadata:
        print("Нет таблиц.")
    else:
        for name in metadata:
            print("-", name)


@handle_db_errors
@log_time
def insert(metadata: dict, table_name: str, values: list,
           table_data: list[dict]) -> list[dict]:
    """Добавляет запись в таблицу."""
    if table_name not in metadata:
        raise KeyError(table_name)

    columns = metadata[table_name][1:]
    if len(values) != len(columns):
        raise ValueError(
            "Количество значений не совпадает с количеством столбцов.")

    record = {}
    for (col_name, col_type), value in zip(columns, values):
        py_type = VALID_TYPES[col_type]
        if col_type == "bool" and isinstance(value, str):
            val_lower = value.lower()
            if val_lower in ("true", "1"):
                value = True
            elif val_lower in ("false", "0"):
                value = False
            else:
                raise ValueError(f"Некорректное значение для bool: {value}")
        try:
            record[col_name] = py_type(value)
        except Exception:
            raise ValueError(
                f"Значение {value} не соответствует типу {col_type}")

    new_id = max([row["ID"] for row in table_data], default=0) + 1
    row = {"ID": new_id, **record}
    table_data.append(row)
    cache_result.invalidate()
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return table_data


@handle_db_errors
@log_time
def select(table_data: list[dict], where: dict | None = None) -> list[dict]:
    """Выбирает записи с кэшированием."""

    cache_key = str(where) if where else "all"

    def compute():
        if not where:
            return table_data
        key, val = next(iter(where.items()))
        norm_val = normalize_value(val)
        return [row for row in table_data if
                normalize_value(row.get(key)) == norm_val]

    return cache_result(cache_key, compute)


@handle_db_errors
def update(
        table_data: list[dict], set_clause: dict, where: dict) -> list[dict]:
    """Обновляет записи по условию."""
    if not where:
        raise ValueError("Условие WHERE обязательно.")

    key, val = next(iter(where.items()))
    norm_val = normalize_value(val)

    updated = 0
    for row in table_data:
        if normalize_value(row.get(key)) == norm_val:
            for set_key, set_val in set_clause.items():
                row[set_key] = normalize_value(set_val)
            updated += 1

    cache_result.invalidate()

    if updated:
        print(f"Обновлено записей: {updated}")
    else:
        print("Подходящих записей не найдено.")
    return table_data


@handle_db_errors
@confirm_action("удаление записей")
def delete(table_data: list[dict], where: dict) -> list[dict]:
    """Удаляет записи по условию."""
    if not where:
        raise ValueError("Условие WHERE обязательно.")

    key, val = next(iter(where.items()))
    norm_val = normalize_value(val)

    before = len(table_data)
    table_data = [row for row in table_data if
                  normalize_value(row.get(key)) != norm_val]
    after = len(table_data)

    cache_result.invalidate()

    if before == after:
        print("Записей для удаления не найдено.")
    else:
        print(f"Удалено записей: {before - after}")
    return table_data


@handle_db_errors
def info(metadata: dict, table_name: str, table_data: list[dict]) -> None:
    """Выводит структуру и статистику таблицы."""
    if table_name not in metadata:
        raise KeyError(table_name)

    cols = ", ".join(f"{n}:{t}" for n, t in metadata[table_name])
    print(f"Таблица: {table_name}")
    print(f"Столбцы: {cols}")
    print(f"Количество записей: {len(table_data)}")
