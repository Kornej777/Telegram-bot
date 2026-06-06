import sqlite3
import logging
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "bot_database.db")

class Tables:

    @staticmethod
    def init_rangs():
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            #Tables.drop_tables()

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS ban_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL UNIQUE,
                    username TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    admin_user TEXT NOT NULL,
                    time DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS unban_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL UNIQUE,
                    username TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    admin_user TEXT NOT NULL,
                    time DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS chats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL UNIQUE,
                    title TEXT NOT NULL,
                    link TEXT NOT NULL
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS rangs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL UNIQUE,
                    username TEXT NOT NULL,
                    rang TEXT NOT NULL
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS admin_junior_try_unban_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL UNIQUE,
                    username TEXT NOT NULL,
                    admin_user TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    admin_id INTENGER NOT NULL,
                    time DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS admin_junior_try_ban_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL UNIQUE,
                    username TEXT NOT NULL,
                    admin_user TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    admin_id INTENGER NOT NULL,
                    time DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            conn.commit()
            conn.close()
            logging.info("✅ Таблицы успешно инициализированы или уже существуют.")
            return True

        except sqlite3.Error as e:
            logging.error(f"❌ Ошибка при создании таблицы 'rangs': {e}")
            return False

    @staticmethod
    def debug_database_info():
        try:
            print(f"🔍 Проверяем базу по пути: {DB_PATH}")
            print(f"📂 Существует ли файл: {os.path.exists(DB_PATH)}")

            if os.path.exists(DB_PATH):
                print(f"📏 Размер файла: {os.path.getsize(DB_PATH)} байт")

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"📊 Таблицы в базе: {tables}")

            for t in tables:
                cursor.execute(f"SELECT * FROM {t[0]}")
                records = cursor.fetchall()
                print(f"📝 Записи в таблице {t[0]}: {records}")

            conn.close()

        except Exception as e:
            print(f"❌ Ошибка при проверке базы: {e}")

    @staticmethod
    def drop_tables():

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            for table in tables:
                table_name = table[0]
                if table_name not in ["sqlite_sequence"]:
                    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                    print(f"Таблица {table_name} удалена.")

            conn.commit()
