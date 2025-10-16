#!/usr/bin/env python3
"""Декораторы и замыкания для управления БД."""

import time
from functools import wraps

import prompt


def handle_db_errors(func):
    """Декоратор: перехватывает ошибки БД
    и пробрасывает их после логирования.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. "
                "Возможно, база данных не инициализирована."
            )
            raise
        except KeyError as e:
            msg = str(e).strip("'\"")
            if msg in (
                    "users", "orders", ...):
                print(f"Ошибка: Таблица '{msg}' уже существует.")
            else:
                print(f"Ошибка: Таблица или столбец {msg} не найден.")
            raise

        except ValueError as e:
            print(f"Ошибка валидации: {e}")
            raise
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
            raise

    return wrapper


def confirm_action(action_name: str):
    """Декоратор-фабрика: спрашивает подтверждение у пользователя."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            answer = prompt.string(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            )
            if answer.lower() != "y":
                print("Операция отменена пользователем.")
                return None
            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    """Декоратор: измеряет время выполнения функции."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        duration = time.monotonic() - start
        print(f"Функция {func.__name__} выполнилась за {duration:.3f} секунд.")
        return result

    return wrapper


def create_cacher():
    """
    Замыкание для кэширования результатов.
    cache_result(key, value_func) — возвращает результат из кэша
    или пересчитывает.
    """
    cache = {}

    def cache_result(key, value_func):
        if key in cache:
            return cache[key]
        result = value_func()
        cache[key] = result
        return result

    def invalidate():
        cache.clear()

    wrapper = cache_result
    wrapper.invalidate = invalidate
    return wrapper
