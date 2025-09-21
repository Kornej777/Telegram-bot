from bot_module.class_verify import Verify
from bot_module.repositories.class_chats_repository import ChatsRepository
from telegram import Update
from telegram.ext import ContextTypes
import sqlite3
import logging
from bot_module.class_warnings import Warnings
import re
from bot_module.class_tables import DB_PATH
from telegram.error import TelegramError

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
            ) or len(context.args) > 2:
                await update.message.reply_text("Использование: Напишите /add_chat ID ссылка")
                return
            chat_id = context.args[0]
            chat_link = context.args[1] if len(context.args) == 2 else '(нет ссылки)'
            chat_info = await context.bot.get_chat(chat_id)
            chat_title = chat_info.title

            if self.verify.is_chat(chat_id):
                await update.message.reply_text("Чат уже в реестре!")
                return
            
            data = {
                'chat_id': chat_id,
                'title': chat_title,
                'link': chat_link
            }

            if self.chats.add(data):
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
            chats = self.chats.get_all_chats()

            if not chats:
                await update.message.reply_text("📋 Реестр чатов пуст")
                return

            response = "📋 Чаты в реестре:\n\n"
            response += "✅ Могут банить:\n"
            response_cant_ban = "❌ НЕ МОГУТ БАНИТЬ:\n"
            count_cant_ban = 0
            for chat in chats:
                if await self.check_ban_permissions(chat[1]):
                    response += f"• {chat[2]} (Ссылка: {chat[3]})\n"
                else:
                    response_cant_ban += f"• {chat[2]} (Ссылка: {chat[3]})\n"
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