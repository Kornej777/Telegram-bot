import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import sqlite3
import logging
import re
from datetime import datetime
from telegram.error import TelegramError

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "bot_database.db")


class BaseRepository:

    def __init__(self, table_name: str):
        self.table_name = table_name

    def delete(self, field: str, value: any) -> bool:

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {self.table_name} WHERE {field} = ?", (value,))
            rows_affected = cursor.rowcount
            conn.commit()
            conn.close()
            return rows_affected > 0

        except Exception as e:
            logging.error(f"Ошибка удаления из {self.table_name}: {e}")
            return False

    def get_by_field(self, field: str, value: any) -> any:

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT * FROM {self.table_name} WHERE {field} = ?", (value,)
            )
            result = cursor.fetchone()
            conn.close()
            return result

        except Exception as e:
            logging.error(f"Ошибка получения из {self.table_name}: {e}")
            return None

    def add(self, id: any, title: str, rang: int = None) -> bool:

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            if not rang:
                cursor.execute(
                    f"""
                INSERT OR REPLACE INTO {self.table_name} 
                (chat_id, title)
                VALUES (?, ?)
                """,
                    (id, title),
                )
            else:
                cursor.execute(
                    f"""
                INSERT OR REPLACE INTO {self.table_name} 
                (user_id, username, rang)
                VALUES (?, ?, ?)
                """,
                    (id, title, rang),
                )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Ошибка добавления в {self.table_name}: {e}")
            return False


class RangsRepository(BaseRepository):

    def __init__(self):
        super().__init__("rangs")

    def delete_user(self, user_id: int) -> bool:
        return self.delete("user_id", user_id)

    def get_user(self, user_id: int) -> any:
        return self.get_by_field("user_id", user_id)

    def upload_rang(self, user_data: dict) -> bool:
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO rangs (user_id, username, rang) VALUES (?, ?, ?)",
                (user_data["user_id"], user_data["username"], user_data["rang"]),
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Ошибка записи в rangs: {e}")
            return False

    def add_rang(self, user_id: int, username: str, rang: int) -> bool:
        existing = self.get_user(user_id)
        if existing:
            return self.upload_rang(
                {"user_id": user_id, "username": username, "rang": rang}
            )
        else:
            return self.add(user_id, username, rang)


class ChatsRepository(BaseRepository):

    def __init__(self):
        super().__init__("chats")

    def delete_chat(self, chat_id: int) -> bool:
        return self.delete("chat_id", chat_id)

    def get_chat(self, chat_id: int) -> any:
        return self.get_by_field("chat_id", chat_id)

    def add_chat(self, chat_id: int, title: str) -> bool:
        return self.add(chat_id, title)


class Tables:
    @staticmethod
    def init_rangs():
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # cursor.execute(f"DROP TABLE IF EXISTS rangs")
            # cursor.execute(f"DROP TABLE IF EXISTS chats")

            cursor.execute(
                """
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL UNIQUE,
                title TEXT NOT NULL
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


class Warnings:
    @staticmethod
    async def not_admin(update: Update):
        return await update.message.reply_text(
            "❌ У вас нет прав для выполнения этой команды."
        )


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


class Admin:

    def __init__(self, verify: Verify, rangs: RangsRepository):
        self.verify = verify
        self.admins = rangs

    async def add(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            if not await self.verify.is_owner(update):
                return await Warnings.not_admin(update)

            if not update.message.reply_to_message:
                if len(context.args) < 2 or context.args[1] not in ["1", "2"]:
                    await update.message.reply_text(
                        "Использование: Напишите /add_admin id ранг (1 или 2)"
                    )
                    return
                else:
                    user_id = context.args[0]
                    rang = context.args[1]
                    try:
                        user = await context.bot.get_chat(user_id)
                        username = (
                            f"@{user.username}" if user.username else f"user_{user_id}"
                        )
                    except Exception as e:
                        username = f"user_{user_id}"
                        logging.error(
                            f"Не удалось получить username для {user_id}: {e}"
                        )
                    if self.admins.add(user_id, username, rang):
                        await update.message.reply_text("✅ Администратор добавлен")
                    else:
                        await update.message.reply_text(
                            "❌ Не удалось добавить администратора."
                        )
                    return
            else:
                if len(context.args) < 1 or context.args[0] not in ["1", "2"]:
                    await update.message.reply_text(
                        "Использование: Ответьте на сообщение и напишите /add_admin ранг (1 или 2)"
                    )
                    return
                target_user = update.message.reply_to_message.from_user
                user_id = target_user.id
                username = (
                    f"@{target_user.username}"
                    if target_user.username
                    else f"user_{user_id}"
                )
                new_rang = context.args[0]

                if self.verify.is_admin(user_id) and not self.verify.can_overwrite_rang(
                    user_id, new_rang
                ):
                    current_rang = self.get_user_rang(user_id)
                    await update.message.reply_text(
                        f"❌ Нельзя понизить ранг пользователя!\n"
                        f"• Текущий ранг: {current_rang}\n"
                        f"• Попытка установить: {new_rang}\n"
                        f"• Можно установить только более высокий ранг ({current_rang+1})"
                    )
                    return

                data = {
                    "user_id": user_id,
                    "username": username,
                    "rang": new_rang,
                }

                if self.admins.upload_rang(data):
                    action = "обновлен" if self.verify.is_admin(user_id) else "добавлен"
                    report_text = (
                        f"✅ Пользователь {username} {action} в списке администраторов.\n"
                        f"• ID: {user_id}\n"
                        f"• Ранг: {new_rang}\n"
                    )
                    await update.message.reply_text(report_text)
                else:
                    await update.message.reply_text(
                        "❌ Не удалось сохранить данные в базу."
                    )

        except Exception as e:
            error_msg = f"Ошибка в add_admin: {str(e)}"
            logging.error(error_msg)
            await update.message.reply_text(
                "❌ Произошла ошибка при выполнении команды."
            )

    def get_user_rang(self, user_id):

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT rang FROM rangs WHERE user_id = ? LIMIT 1",
                (user_id,),
            )

            result = cursor.fetchone()
            conn.close()

            return int(result[0]) if result else None

        except Exception as e:
            logging.error(f"Ошибка получения ранга пользователя: {e}")
            return None

    async def remove(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:

            if not await self.verify.is_owner(update):
                return await Warnings.not_admin(update)

            if not update.message.reply_to_message:
                if len(context.args) < 1:
                    await update.message.reply_text(
                        "❌ Эта команда работает только как ответ на сообщение пользователя.\n\n"
                        "Использование: Ответьте на сообщение администратора и напишите /remove_admin"
                    )
                    return
                else:
                    user_id = context.args[0]
                    user = await context.bot.get_chat(user_id)
                    username = f"@{user.username}" if user.username else "нет username"
                    if not self.verify.is_admin(user_id):
                        await update.message.reply_text(
                            "❌ Этот пользователь не является администратором!"
                        )
                        return
                    if self.admins.delete_user(user_id):
                        report_text = (
                            f"✅ Пользователь {username} удален из списка администраторов.\n"
                            f"• ID: {user_id}\n"
                            f"• Теперь у него обычные права пользователя\n"
                        )
                        await update.message.reply_text(report_text)
                        return
                    else:
                        await update.message.reply_text(
                            "❌ Не удалось удалить администратора из базы данных."
                        )
                        return

            target_user = update.message.reply_to_message.from_user
            user_id = target_user.id
            username = (
                f"@{target_user.username}"
                if target_user.username
                else f"user_{user_id}"
            )

            if not self.verify.is_admin(user_id):
                await update.message.reply_text(
                    "❌ Этот пользователь не является администратором!"
                )
                return

            if self.admins.delete_user("user_id", user_id):
                report_text = (
                    f"✅ Пользователь {username} удален из списка администраторов.\n"
                    f"• ID: {user_id}\n"
                    f"• Теперь у него обычные права пользователя\n"
                )
                await update.message.reply_text(report_text)
            else:
                await update.message.reply_text(
                    "❌ Не удалось удалить администратора из базы данных."
                )

        except Exception as e:
            error_msg = f"Ошибка в remove_admin: {str(e)}"
            logging.error(error_msg)
            await update.message.reply_text(
                "❌ Произошла ошибка при выполнении команды."
            )

    async def list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute("SELECT user_id, username, rang FROM rangs ORDER BY rang")
            admins = cursor.fetchall()

            conn.close()

            if not admins:
                await update.message.reply_text("📋 Список администраторов пуст")
                return

            response = "📋 Список администраторов:\n\n"
            for admin in admins:
                response += f"• {admin[1]} (ID: {admin[0]}) - Ранг: {admin[2]}\n"

            await update.message.reply_text(response)

        except Exception as e:
            logging.error(f"❌ Ошибка получения списка администраторов: {e}")
            await update.message.reply_text("❌ Ошибка при получении списка")


class Chats:

    def __init__(self, verify: Verify, chats: ChatsRepository, bot):
        self.verify = verify
        self.chats = chats
        self.bot = bot

    async def add(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            if not await self.verify.is_owner(update):
                return await Warnings.not_admin(update)

            if len(context.args) < 1 or not re.match(
                r"^-100\d+$|^-\d+$", context.args[0]
            ):
                await update.message.reply_text("Использование: Напишите /add_chat ID")
                return
            chat_id = context.args[0]
            chat_info = await context.bot.get_chat(chat_id)
            chat_title = chat_info.title

            if self.verify.is_chat(chat_id):
                await update.message.reply_text("Чат уже в реестре!")
                return

            if self.chats.add(chat_id, chat_title):
                await update.message.reply_text(
                    f"✅ Чат {chat_title} добавлен в реестр!"
                )
                return True
            else:
                await update.message.reply_text(
                    f"❌ Ошибка добавления чата {chat_title}"
                )
                return False

        except Exception as e:
            error_msg = f"Ошибка в add_chat: {str(e)}"
            logging.error(error_msg)
            await update.message.reply_text("❌ Чат не найден или бот не имеет доступа")

    async def remove(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            if not await self.verify.is_owner(update):
                return await Warnings.not_admin(update)
            if len(context.args) < 1 or not re.match(
                r"^-100\d+$|^-\d+$", context.args[0]
            ):
                await update.message.reply_text(
                    "Использование: Напишите /remove_chat ID"
                )
                return
            chat_id = context.args[0]
            chat_info = await context.bot.get_chat(chat_id)
            chat_title = chat_info.title
            if not self.verify.is_chat(chat_id):
                await update.message.reply_text("❌ Этого чата и так нет в реестре!")
                return
            if self.chats.delete_chat(chat_id):
                report_text = (
                    f"✅ Чат {chat_title} удален из реестра.\n" f"• ID: {chat_id}\n"
                )
                await update.message.reply_text(report_text)
                return
            else:
                await update.message.reply_text("❌ Не удалось удалить чат из реестра.")
                return

        except Exception as e:
            error_msg = f"Ошибка в remove_chat: {str(e)}"
            logging.error(error_msg)
            await update.message.reply_text(
                "❌ Чат не найден или бот не имеет доступа."
            )

    async def list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute("SELECT chat_id, title FROM chats ORDER BY id")
            chats = cursor.fetchall()

            conn.close()

            if not chats:
                await update.message.reply_text("📋 Реестр чатов пуст")
                return

            response = "📋 Чаты в реестре:\n\n"
            response += "✅ Могут банить:\n"
            response_cant_ban = "❌ НЕ МОГУТ БАНИТЬ:\n"
            count_cant_ban = 0
            for chat in chats:
                if await self.check_ban_permissions(chat[0]):
                    response += f"• {chat[1]} (ID: {chat[0]})\n"
                else:
                    response_cant_ban += f"• {chat[1]} (ID: {chat[0]})\n"
                    count_cant_ban += 1
            if count_cant_ban > 0:
                response += response_cant_ban

            await update.message.reply_text(response)

        except Exception as e:
            logging.error(f"❌ Ошибка получения списка администраторов: {e}")
            await update.message.reply_text("❌ Ошибка при получении списка")

    async def check_ban_permissions(self, chat_id):
        try:
            bot_member = await self.bot.get_chat_member(chat_id, self.bot.id)

            if bot_member.status not in ["administrator", "creator"]:
                return False

            if hasattr(bot_member, "can_restrict_members"):
                return bot_member.can_restrict_members
            return False

        except TelegramError as e:
            print(f"Ошибка проверки прав: {e}")
            return False
