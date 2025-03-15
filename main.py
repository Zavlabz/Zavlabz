import sqlite3

class TableData:
    def __init__(self, database_name, table_name):
        self.database_name = database_name
        self.table_name = table_name

    def __len__(self):
        # Получаем количество записей в таблице
        with sqlite3.connect(self.database_name) as conn:
            cursor = conn.cursor()
            query = f"SELECT COUNT(*) FROM {self.table_name}"
            cursor.execute(query)
            count = cursor.fetchone()[0]
        return count

    def __getitem__(self, key):
        # Получаем запись с полем 'name', равным key
        with sqlite3.connect(self.database_name) as conn:
            conn.row_factory = sqlite3.Row  # Позволяет обращаться к столбцам по имени
            cursor = conn.cursor()
            query = f"SELECT * FROM {self.table_name} WHERE name = ?"
            cursor.execute(query, (key,))
            row = cursor.fetchone()
            if row is None:
                raise KeyError(f"Запись с именем '{key}' не найдена")
            return dict(row)

    def __contains__(self, key):
        # Проверяем наличие записи с полем 'name'
        try:
            _ = self[key]
            return True
        except KeyError:
            return False

    def __iter__(self):
        # Итерация по записям таблицы без загрузки всей таблицы в память
        with sqlite3.connect(self.database_name) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            query = f"SELECT * FROM {self.table_name}"
            cursor.execute(query)
            for row in cursor:
                yield dict(row)

# Пример тестового кода
if __name__ == "__main__":
    # Создаём экземпляр для таблицы 'presidents'
    presidents = TableData(database_name='example.sqlite', table_name='presidents')

    # Выводим общее количество записей в таблице
    print("Количество записей в таблице presidents:", len(presidents))

    # Задаём имя для проверки (пример: 'Yeltsin')
    sample_name = 'Yeltsin'
    print(f"Существует ли запись с именем '{sample_name}'?", sample_name in presidents)

    # Выводим запись с именем 'Yeltsin'
    try:
        record = presidents[sample_name]
        print(f"Запись для '{sample_name}':", record)
    except KeyError as e:
        print(e)

    # Итерация по таблице и вывод всех имен
    print("Список имён всех записей:")
    for rec in presidents:
        print(rec['name'])
