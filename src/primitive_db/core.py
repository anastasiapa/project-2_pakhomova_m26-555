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


def drop_table(metadata, table_name):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]

    print(f'Таблица "{table_name}" успешно удалена.')

    return metadata