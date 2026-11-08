from primitive_db.decorators import confirm_action, handle_db_errors, log_time


@handle_db_errors
def create_table(metadata, table_name, columns):
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"

    if not table_name or not all(char in allowed_chars for char in table_name):
        print(f"Некорректное значение: {table_name}. Попробуйте снова.")
        return metadata

    table_columns = {"ID": "int"}

    for column in columns:
        if column.count(":") != 1:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return metadata

        name, data_type = column.split(":")

        if (
            not name
            or name in table_columns
            or data_type not in ("int", "str", "bool")
        ):
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return metadata

        table_columns[name] = data_type

    metadata[table_name] = table_columns

    column_description = ", ".join(
        f"{name}:{data_type}" for name, data_type in table_columns.items()
    )

    print(
        f'Таблица "{table_name}" успешно создана '
        f"со столбцами: {column_description}"
    )

    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]

    print(f'Таблица "{table_name}" успешно удалена.')

    return metadata


def check_value_type(value, data_type):
    if data_type == "int":
        return type(value) is int
    elif data_type == "str":
        return type(value) is str
    elif data_type == "bool":
        return type(value) is bool

    return False


@handle_db_errors
@log_time
def insert(metadata, table_name, table_data, values):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None

    columns = metadata[table_name]
    column_names = [name for name in columns if name != "ID"]

    if len(values) != len(column_names):
        print(f"Некорректное значение: {values}. Попробуйте снова.")
        return None

    for name, value in zip(column_names, values):
        data_type = columns[name]

        if not check_value_type(value, data_type):
            print(f"Некорректное значение: {value}. Попробуйте снова.")
            return None

    new_id = 1

    for record in table_data:
        if record["ID"] >= new_id:
            new_id = record["ID"] + 1

    new_record = {"ID": new_id}

    for name, value in zip(column_names, values):
        new_record[name] = value

    table_data.append(new_record)

    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')

    return table_data


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    if where_clause is None:
        return table_data

    result = []

    for record in table_data:
        matches = True

        for column, value in where_clause.items():
            if record.get(column) != value:
                matches = False
                break

        if matches:
            result.append(record)

    return result


@handle_db_errors
def update(table_data, set_clause, where_clause):
    for record in table_data:
        matches = True

        for column, value in where_clause.items():
            if record.get(column) != value:
                matches = False
                break

        if matches:
            for column, value in set_clause.items():
                record[column] = value

    return table_data


@handle_db_errors
@confirm_action("удаление записей")
def delete(table_data, where_clause):
    result = []

    for record in table_data:
        matches = True

        for column, value in where_clause.items():
            if record.get(column) != value:
                matches = False
                break

        if not matches:
            result.append(record)

    return result