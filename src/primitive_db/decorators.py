import time


def handle_db_errors(func):
    """Обрабатывает ошибки при выполнении операций с базой данных."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: Файл данных не найден.")
        except KeyError as error:
            print(f"Ошибка: Таблица или столбец {error} не найден.")
        except ValueError as error:
            print(f"Ошибка валидации: {error}")
        except Exception as error:
            print(f"Произошла непредвиденная ошибка: {error}")

    return wrapper


def confirm_action(action_name):
    """Запрашивает подтверждение перед выполнением операции."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            answer = input(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            )

            if answer.strip().lower() != "y":
                print("Операция отменена.")
                return None

            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    """Измеряет время выполнения функции."""

    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        finish_time = time.monotonic() - start_time

        print(f"Функция {func.__name__} выполнилась за {finish_time:.3f} секунд")
        return result

    return wrapper


def create_cacher():
    """Создаёт кэш для результатов запросов."""

    cache = {}

    def cache_result(key, value_func):
        if key in cache:
            return cache[key]

        result = value_func()
        cache[key] = result
        return result

    return cache_result