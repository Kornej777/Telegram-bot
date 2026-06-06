import logging
import sqlite3
from bot.tables import DB_PATH

class BaseRepository:

    def __init__(self, table_name: str):
        self.table_name = table_name

    def delete(self, field: str, value: any) -> bool:

        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(f"DELETE FROM {self.table_name} WHERE {field} = ?", (value,))
                rows_affected = cursor.rowcount
                conn.commit()
            return rows_affected > 0

        except Exception as e:
            logging.error(f"Ошибка удаления из {self.table_name}: {e}")
            return False
        
    def delete_all(self):

        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(f"DELETE FROM {self.table_name}")
                conn.commit()
            return True
        except Exception as e:
            logging.error(f"Ошибка удаления из {self.table_name}: {e}")
            return False

    def get_by_field(self, field: str, value: any) -> any:

        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    f"SELECT * FROM {self.table_name} WHERE {field} = ?", (value,)
                )
                result = cursor.fetchone()
            return result

        except Exception as e:
            logging.error(f"Ошибка получения из {self.table_name}: {e}")
            return None

    def add(self, data: dict) -> bool:

        try:

            fields = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            values = tuple(data.values())

            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    f"INSERT OR REPLACE INTO {self.table_name} ({fields}) VALUES ({placeholders})",
                    values
                )
                conn.commit()
            return True
            
        except Exception as e:
            logging.error(f"Ошибка добавления в {self.table_name}: {e}")
            return False
        
    def get_all(self):
        
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {self.table_name} ORDER BY id")
            return cursor.fetchall()