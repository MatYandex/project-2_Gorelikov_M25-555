#!/usr/bin/env python3
VALID_TYPES = {"int", "str", "bool"}


def create_table(metadata: dict, table_name: str, columns: list[str]) -> dict:
    """
    Создаёт таблицу с указанными столбцами.
    Автоматически добавляет ID:int.
    """
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
            print(f"Некорректный тип: {col_type}."
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
