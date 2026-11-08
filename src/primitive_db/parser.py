def parse_value(value):
    """Преобразует строку в значение нужного типа."""

    value = value.strip()

    if len(value) >= 2 and value.startswith('"') and value.endswith('"'):
        return value[1:-1]

    if value.lower() == "true":
        return True

    if value.lower() == "false":
        return False

    try:
        return int(value)
    except ValueError:
        raise ValueError(
            f"Некорректное значение: {value}. Попробуйте снова."
        ) from None
    

def parse_condition(condition):
    """Разбирает условие на равенство."""

    if "=" not in condition:
        raise ValueError(
            f"Некорректное значение: {condition}. Попробуйте снова."
        )

    column, value = condition.split("=", 1)

    column = column.strip()
    value = value.strip()

    if not column or not value:
        raise ValueError(
            f"Некорректное значение: {condition}. Попробуйте снова."
        )

    return {column: parse_value(value)}


def parse_insert_values(text):
    """Разбирает значения для добавления записи."""
    
    text = text.strip()

    if not text.startswith("(") or not text.endswith(")"):
        raise ValueError(f"Некорректное значение: {text}. Попробуйте снова.")

    content = text[1:-1]
    values = []
    current_value = ""
    in_quotes = False

    for char in content:
        if char == '"':
            in_quotes = not in_quotes

        if char in "()" and not in_quotes:
            raise ValueError(f"Некорректное значение: {text}. Попробуйте снова.")

        if char == "," and not in_quotes:
            values.append(current_value.strip())
            current_value = ""
        else:
            current_value += char

    if in_quotes:
        raise ValueError(f"Некорректное значение: {text}. Попробуйте снова.")

    values.append(current_value.strip())

    if any(not value for value in values):
        raise ValueError(f"Некорректное значение: {text}. Попробуйте снова.")

    return [parse_value(value) for value in values]