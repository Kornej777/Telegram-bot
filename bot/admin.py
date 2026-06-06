from telegram import Update
from telegram.ext import ContextTypes
import sqlite3
import logging
from bot.verify import Verify
from bot.repositories.rangs_repo import RangsRepository
from bot.warnings import Warnings
from bot.tables import DB_PATH


class Admin:

    def __init__(self, verify: Verify, rangs: RangsRepository):
        self.verify = verify
        self.admins = rangs

    async def add(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            if not await self.verify.is_owner(update):
                return await Warnings.not_admin(update)

            if not update.message.reply_to_message:

                if len(context.args) < 1:
                    await update.message.reply_text(
                        "• Использование: Напишите /add_admin id ранг (1 или 2)"
                    )
                    return
                
                else:
                    user_id = context.args[0]
                    try:
                        rang = context.args[1] if context.args[1] in ['1', '2'] else '1'
                    except:
                        rang = '1'
                    rang_title = 'Младший' if int(rang) == 1 else 'Старший'
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

                    data = {
                        'user_id': user_id,
                        'username': username,
                        'rang': rang
                    }

                    if self.admins.add_rang(data):
                        action = 'обновлен' if self.verify.is_admin(user_id) else 'добавлен'
                        await update.message.reply_text(
                            f"✅ Администратор {username} {action}.\n"
                            f"Ранг: {rang} — {rang_title}"                    
                        )
                    else:
                        await update.message.reply_text(
                            "❌ Не удалось добавить администратора."
                        )
                    return
            else:
                try:
                    rang = context.args[0] if context.args[0] in ['1', '2'] else '1'
                except:
                    rang = '1'
                rang_title = 'Младший' if int(rang) == 1 else 'Старший'
                target_user = update.message.reply_to_message.from_user
                user_id = target_user.id
                username = (
                    f"@{target_user.username}"
                    if target_user.username
                    else f"user_{user_id}"
                )

                data = {
                    'user_id': user_id,
                    'username': username,
                    'rang': rang
                }

                if self.admins.add_rang(data):
                    action = 'обновлен' if self.verify.is_admin(user_id) else 'добавлен'
                    await update.message.reply_text(
                        f"✅ Администратор {username} {action}.\n"
                        f"Ранг: {rang} — {rang_title}"                    
                    )
                else:
                    await update.message.reply_text(
                        "❌ Не удалось добавить администратора."
                    )

        except Exception as e:
            error_msg = f"Ошибка в add_admin: {str(e)}"
            logging.error(error_msg)
            await update.message.reply_text(
                "❌ Произошла ошибка при выполнении команды."
            )

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
            admins = self.admins.get_all_rangs()
            bot_owner = self.admins.get_user(5592317446)
            response = "📋 Список администраторов"
            senior_admins = []
            junior_admins = []

            if not admins:
                await update.message.reply_text(f"{response} пуст")
                return

            response += ":\n\n"
            for admin in admins:
                if int(admin[3]) == 1:
                    junior_admins.append(f"• {admin[2]} (ID: {admin[1]})\n")
                else:
                    if admin[1] in [5592317446]:
                        continue
                    senior_admins.append(f"• {admin[2]} (ID: {admin[1]})\n")

            response += (
                '👑 Владелец бота:\n'
                f'• {bot_owner[2]} (ID: {bot_owner[1]})\n\n'
            )

            if senior_admins:
                response += (
                    '🔹 Старшие администраторы:\n'
                )
                for admin in senior_admins:
                    response += admin
                response += '\n'

            if junior_admins:
                response += (
                    '🔸 Младшие администраторы:\n'
                )
                for admin in junior_admins:
                    response += admin

            await update.message.reply_text(response)

        except Exception as e:
            logging.error(f"❌ Ошибка получения списка администраторов: {e}")
            await update.message.reply_text("❌ Ошибка при получении списка")
