import shlex

import prompt
from prettytable import PrettyTable

from primitive_db.constants import META_FILE
from primitive_db.core import (
    check_value_type,
    create_table,
    delete,
    drop_table,
    insert,
    select,
    update,
)
from primitive_db.decorators import create_cacher
from primitive_db.parser import parse_condition, parse_insert_values
from primitive_db.utils import (
    delete_table_data,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def print_help():
    """Выводит справку по командам."""

    print("\n***Процесс работы с таблицей***")

    print("\nФункции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print(
        "<command> insert into <имя_таблицы> values "
        "(<значение1>, <значение2>, ...) - создать запись."
    )
    print(
        "<command> select from <имя_таблицы> where <столбец> = <значение>"
        " - прочитать записи по условию."
    )
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print(
        "<command> update <имя_таблицы> set <столбец1> = <новое_значение1>"
        " where <столбец_условия> = <значение_условия> - обновить запись."
    )
    print(
        "<command> delete from <имя_таблицы> where <столбец> = <значение>"
        " - удалить запись."
    )
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run():
    """Запускает обработку команд пользователя."""

    print_help()
    cache_result = create_cacher()

    while True:
        metadata = load_metadata(META_FILE)
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
                save_metadata(META_FILE, metadata)

        elif command == "drop_table":
            if len(args) != 2:
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue

            table_name = args[1]
            
            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue

            updated_metadata = drop_table(metadata, table_name)

            if updated_metadata is not None:
                metadata = updated_metadata
                save_metadata(META_FILE, metadata)
                delete_table_data(table_name)
                cache_result = create_cacher()

        elif command == "insert":
            parts = user_input.split(maxsplit=3)

            if len(parts) != 4 or parts[1] != "into":
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue

            table_name = parts[2]
            value_parts = parts[3].split(maxsplit=1)

            if len(value_parts) != 2 or value_parts[0] != "values":
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue

            try:
                values = parse_insert_values(value_parts[1])
            except ValueError as error:
                print(error)
                continue

            table_data = load_table_data(table_name)
            updated_data = insert(metadata, table_name, table_data, values)

            if updated_data is not None:
                save_table_data(table_name, updated_data)
                cache_result = create_cacher()
        
        elif command == "select":
            parts = user_input.split(maxsplit=4)

            if len(parts) not in (3, 5) or parts[1] != "from":
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue

            table_name = parts[2]

            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue

            where_clause = None

            if len(parts) == 5:
                if parts[3] != "where":
                    print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                    continue

                try:
                    where_clause = parse_condition(parts[4])
                except ValueError as error:
                    print(error)
                    continue

                column, value = next(iter(where_clause.items()))

                if (
                    column not in metadata[table_name]
                    or not check_value_type(value, metadata[table_name][column])
                ):
                    print(f"Некорректное значение: {parts[4]}. Попробуйте снова.")
                    continue

            table_data = load_table_data(table_name)
            where_key = tuple(sorted(where_clause.items())) if where_clause else None
            cache_key = (table_name, where_key)

            selected_data = cache_result(
                cache_key,
                lambda: select(table_data, where_clause),
                )

            table = PrettyTable()
            table.field_names = list(metadata[table_name].keys())

            for record in selected_data:
                row = [record[name] for name in table.field_names]
                table.add_row(row)

            print(table)
        
        elif command == "update":
            parts = user_input.split(maxsplit=3)

            if len(parts) != 4 or parts[2] != "set":
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue

            table_name = parts[1]

            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue

            conditions = parts[3].rsplit(" where ", 1)

            if len(conditions) != 2:
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue

            try:
                set_clause = parse_condition(conditions[0])
                where_clause = parse_condition(conditions[1])
            except ValueError as error:
                print(error)
                continue

            set_column, set_value = next(iter(set_clause.items()))
            where_column, where_value = next(iter(where_clause.items()))

            columns = metadata[table_name]

            if (
                set_column not in columns
                or set_column == "ID"
                or where_column not in columns
                or not check_value_type(set_value, columns[set_column])
                or not check_value_type(where_value, columns[where_column])
            ):
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue

            table_data = load_table_data(table_name)

            updated_ids = []

            for record in table_data:
                if record.get(where_column) == where_value:
                    updated_ids.append(record["ID"])

            if updated_ids:
                updated_data = update(table_data, set_clause, where_clause)
                save_table_data(table_name, updated_data)
                cache_result = create_cacher()

                for record_id in updated_ids:
                    print(
                        f'Запись с ID={record_id} в таблице '
                        f'"{table_name}" успешно обновлена.'
                    )
        
        elif command == "delete":
            parts = user_input.split(maxsplit=4)

            if (
                len(parts) != 5
                or parts[1] != "from"
                or parts[3] != "where"
            ):
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue

            table_name = parts[2]

            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue

            try:
                where_clause = parse_condition(parts[4])
            except ValueError as error:
                print(error)
                continue

            column, value = next(iter(where_clause.items()))

            if (
                column not in metadata[table_name]
                or not check_value_type(value, metadata[table_name][column])
            ):
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue

            table_data = load_table_data(table_name)
            deleted_ids = []

            for record in table_data:
                if record.get(column) == value:
                    deleted_ids.append(record["ID"])

            if deleted_ids:
                updated_data = delete(table_data, where_clause)

                if updated_data is not None:
                    save_table_data(table_name, updated_data)
                    cache_result = create_cacher()

                    for record_id in deleted_ids:
                        print(
                            f"Запись с ID={record_id} успешно удалена "
                            f'из таблицы "{table_name}".'
                            )

        elif command == "info":
            if len(args) != 2:
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue

            table_name = args[1]

            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue

            columns = metadata[table_name]
            column_description = ", ".join(
                f"{name}:{data_type}" for name, data_type in columns.items()
            )

            table_data = load_table_data(table_name)

            print(f"Таблица: {table_name}")
            print(f"Столбцы: {column_description}")
            print(f"Количество записей: {len(table_data)}")
        else:
            print(f"Функции {command} нет. Попробуйте снова.")