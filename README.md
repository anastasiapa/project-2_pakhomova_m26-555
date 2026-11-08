# Примитивная база данных

## Управление таблицами

Программа позволяет создавать, просматривать и удалять таблицы.

Поддерживаемые типы данных: `int`, `str`, `bool`.

### Команды

- `create_table <имя_таблицы> <столбец1:тип> ...` — создать таблицу.
- `list_tables` — показать список таблиц.
- `drop_table <имя_таблицы>` — удалить таблицу.
- `help` — показать справку.
- `exit` — выйти из программы.

### Пример использования

```text
create_table users name:str age:int is_active:bool
Таблица "users" успешно создана со столбцами: ID:int, name:str, age:int, is_active:bool

list_tables
- users

drop_table users
Таблица "users" успешно удалена.
```

## Демонстрация работы программы

[![Демонстрация работы базы данных](https://asciinema.org/a/a79AxuIZUzGut6fQ.svg)](https://asciinema.org/a/a79AxuIZUzGut6fQ)