#!/usr/bin/env python3
"""Основная логика управления таблицами и CRUD."""

VALID_TYPES = {"int": int, "str": str, "bool": bool}


def create_table(metadata: dict, table_name: str, columns: list[str]) -> dict:
    """Создаёт таблицу с указанными столбцами."""
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    table_columns = [("ID", "int")]
    for col in columns:
        try:
            name, col_type = col.split(":")
        except ValueError:
            print(f"Некорректное значение: {col}. Попробуйте снова.")
            return metadata
        if col_type not in VALID_TYPES:
            print(
                f"Некорректный тип: {col_type}."
                f" Допустимые: {', '.join(VALID_TYPES)}.")
            return metadata
        table_columns.append((name, col_type))

    metadata[table_name] = table_columns
    print(
        f'Таблица "{table_name}" успешно создана со столбцами: '
        + ", ".join(f"{n}:{t}" for n, t in table_columns)
    )
    return metadata


def drop_table(metadata: dict, table_name: str) -> dict:
    """Удаляет таблицу, если она существует."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata
    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata: dict) -> None:
    """Выводит список таблиц."""
    if not metadata:
        print("Нет таблиц.")
    else:
        for name in metadata:
            print("-", name)


# ---------- CRUD ----------

def insert(metadata: dict, table_name: str, values: list,
           table_data: list[dict]) -> list[dict]:
    """Добавляет запись в таблицу."""
    if table_name not in metadata:
        print(f'Ошибка: таблица "{table_name}" не существует.')
        return table_data

    columns = metadata[table_name][1:]  # без ID
    if len(values) != len(columns):
        print("Количество значений не совпадает с количеством столбцов.")
        return table_data

    # проверка типов
    record = {}
    for (col_name, col_type), value in zip(columns, values):
        py_type = VALID_TYPES[col_type]
        try:
            if col_type == "bool":
                if isinstance(value, str):
                    val_lower = value.lower()
                    if val_lower in ("true", "1"):
                        value = True
                    elif val_lower in ("false", "0"):
                        value = False
                    else:
                        print(
                            f"Ошибка: значение {value}"
                            f" не соответствует типу bool.")
                        return table_data
            record[col_name] = py_type(value)
        except ValueError:
            print(
                f"Ошибка: значение {value} не соответствует типу {col_type}.")
            return table_data

    new_id = max([row["ID"] for row in table_data], default=0) + 1
    record["ID"] = new_id
    # порядок полей: сначала ID, потом остальные
    row = {"ID": new_id, **{k: record[k] for k, _ in columns}}
    table_data.append(row)
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return table_data


def select(table_data: list[dict], where: dict | None = None) -> list[dict]:
    """Выбирает записи."""
    if not where:
        return table_data
    key, val = next(iter(where.items()))
    return [row for row in table_data if str(row.get(key)) == str(val)]


def update(
        table_data: list[dict], set_clause: dict, where: dict) -> list[dict]:
    """Обновляет записи по условию."""
    key, val = next(iter(where.items()))
    updated = 0
    for row in table_data:
        if str(row.get(key)) == str(val):
            for set_key, set_val in set_clause.items():
                row[set_key] = set_val
            updated += 1
    if updated:
        print(f"Обновлено записей: {updated}")
    else:
        print("Подходящих записей не найдено.")
    return table_data


def delete(table_data: list[dict], where: dict) -> list[dict]:
    """Удаляет записи по условию."""
    key, val = next(iter(where.items()))
    before = len(table_data)
    table_data = [row for row in table_data if str(row.get(key)) != str(val)]
    after = len(table_data)
    if before == after:
        print("Записей для удаления не найдено.")
    else:
        print(f"Удалено записей: {before - after}")
    return table_data


def info(metadata: dict, table_name: str, table_data: list[dict]) -> None:
    """Выводит структуру и статистику таблицы."""
    if table_name not in metadata:
        print(f'Таблица "{table_name}" не существует.')
        return
    cols = ", ".join(f"{n}:{t}" for n, t in metadata[table_name])
    print(f"Таблица: {table_name}")
    print(f"Столбцы: {cols}")
    print(f"Количество записей: {len(table_data)}")
