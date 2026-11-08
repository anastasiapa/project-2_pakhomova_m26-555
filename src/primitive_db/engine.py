import shlex

import prompt

from primitive_db.core import create_table, drop_table
from primitive_db.utils import load_metadata, save_metadata


def print_help():
    """Выводит справку по командам."""

    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run():
    print_help()

    while True:
        metadata = load_metadata("db_meta.json")
        user_input = prompt.string("Введите команду: ")

        try:
            args = shlex.split(user_input)
        except ValueError:
            print(f"Некорректное значение: {user_input}. Попробуйте снова.")
            continue

        if not args:
            continue

        command = args[0]

        if command == "exit":
            if len(args) == 1:
                break
            print(f"Некорректное значение: {user_input}. Попробуйте снова.")

        elif command == "help":
            if len(args) == 1:
                print_help()
            else:
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")

        elif command == "list_tables":
            if len(args) != 1:
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue

            for table_name in metadata:
                print(f"- {table_name}")

        elif command == "create_table":
            if len(args) < 3:
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue

            table_name = args[1]
            columns = args[2:]

            create_table(metadata, table_name, columns)

            if table_name in metadata:
                save_metadata("db_meta.json", metadata)

        elif command == "drop_table":
            if len(args) != 2:
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue

            table_name = args[1]
            table_exists = table_name in metadata

            drop_table(metadata, table_name)

            if table_exists:
                save_metadata("db_meta.json", metadata)

        else:
            print(f"Функции {command} нет. Попробуйте снова.")