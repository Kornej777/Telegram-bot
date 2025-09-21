import sqlite3
import logging
import os
from dotenv import load_dotenv
from telegram import Update
from bot_module.class_enum import PunishmentType
from bot_module.class_tables import DB_PATH

class Verify:

    def __init__(self):
        self.owner = [5592317446]

    def bot_token(self):
        load_dotenv()
        return os.getenv("BOT_TOKEN")

    async def is_owner(self, update: Update):
        user = update.effective_user

        return user and user.id in self.owner

    def is_admin(self, user_id, rang=1):

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='rangs'"
            )
            if cursor.fetchone() is None:
                logging.error("Таблица 'rangs' не существует в базе данных.")
                return False

            cursor.execute(
                """
                SELECT rang FROM rangs WHERE user_id = ? LIMIT 1
            """,
                (user_id,),
            )
            result = cursor.fetchone()
            conn.close()

            if result is None:
                return False

            user_rang = int(result[0])

            return user_rang >= rang

        except Exception as e:
            logging.error(f"Ошибка проверки пользователя: {e}")
            return False

    def is_chat(self, chat_id):

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='chats'"
            )
            if cursor.fetchone() is None:
                logging.error("Таблица 'chats' не существует в базе данных.")
                return False

            cursor.execute(
                """
                SELECT chat_id FROM chats WHERE chat_id = ? LIMIT 1
            """,
                (chat_id,),
            )
            result = cursor.fetchone()
            conn.close()

            if result is None:
                return False
            else:
                return True

        except Exception as e:
            logging.error(f"Ошибка проверки пользователя: {e}")
            return False

    def can_overwrite_rang(self, user_id, new_rang):

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT rang FROM rangs WHERE user_id = ? LIMIT 1",
                (user_id,),
            )

            result = cursor.fetchone()
            conn.close()

            if result is None:
                return True

            current_rang = int(result[0])
            new_rang_int = int(new_rang)

            return new_rang_int > current_rang

        except Exception as e:
            logging.error(f"Ошибка проверки перезаписи ранга: {e}")
            return False

    def _is_has_try_pynishment(self, user_id, action: PunishmentType) -> bool:

        if action == PunishmentType.BAN:
            table = "admin_junior_try_ban_log"
        else:
            table = "admin_junior_try_unban_log"

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                SELECT user_id FROM {table} WHERE user_id = ? LIMIT 1
                """,
                (user_id,),
            )
            result = cursor.fetchone()

        if result:
            return True
        else:
            return False

    def _is_already_try(self, admin_id, action: PunishmentType) -> bool:

        if action == PunishmentType.BAN:
            table = "admin_junior_try_ban_log"
        else:
            table = "admin_junior_try_unban_log"

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                SELECT admin_id FROM {table} WHERE admin_id = ? LIMIT 1
                """,
                (admin_id,),
            )
            result = cursor.fetchone()

        if result:
            return True
        else:
            return False