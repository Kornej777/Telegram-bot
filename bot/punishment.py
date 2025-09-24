from telegram import Update
from telegram.ext import ContextTypes
from bot.verify import Verify
from bot.warnings import Warnings
import logging
import os
import re
from bot.punishment_type import PunishmentType
from bot.repositories.chats_repo import ChatsRepository
from bot.repositories.ban_log_repo import BanLogRepository
from bot.repositories.unban_log_repo import UnbanLogRepository
from bot.repositories.junior_ban_repo import JuniorBanRepository
from bot.repositories.junior_unban_repo import JuniorUnbanRepository

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "bot_database.db")


class Punishment:

    def __init__(
        self,
        verify: Verify,
        chats: ChatsRepository,
        ban_repo: BanLogRepository,
        unban_repo: UnbanLogRepository,
        jun_ban_repo: JuniorBanRepository,
        jun_unban_repo: JuniorUnbanRepository,
    ):
        self.verify = verify
        self.chats = chats
        self.ban_repo = ban_repo
        self.unban_repo = unban_repo
        self.jun_ban_repo = jun_ban_repo
        self.jun_unban_repo = jun_unban_repo

    async def _command(
        self,
        context: ContextTypes.DEFAULT_TYPE,
        action: PunishmentType,
        id_user: int,
        username: str,
    ):

        chats = self.chats.get_all_chats()

        agreed_chats = []
        failed_chats = []

        for chat in chats:

            try:
                if action == PunishmentType.BAN:

                    await context.bot.ban_chat_member(chat_id=chat[1], user_id=id_user)
                    agreed_chats.append(chat[2])
                    logging.info(f"Успешно забанен {username} в {chat[2]}")

                else:

                    await context.bot.unban_chat_member(
                        chat_id=chat[1], user_id=id_user
                    )
                    agreed_chats.append(chat[2])
                    logging.info(f"Успешно разбанен {username} в {chat[2]}")

            except Exception as e:
                logging.error(f"Ошибка бана {username} в чате {chat[2]}: {e}")
                try:
                    failed_chats.append(f"{chat[2]}: {str(e)}")
                except:
                    failed_chats.append(f"Неизвестный чат ({chat[2]}): {str(e)}")

        return agreed_chats, failed_chats

    async def blacklist(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, action: PunishmentType
    ):
        old_admin_user = None
        admin_id = update.effective_user.id
        admin_user = (
            f"@{update.effective_user.username}"
            if update.effective_user.username
            else f"user_{admin_id}"
        )

        repo, jun_repo, prefix, word = self._get_repo_and_prefix(action)

        if not update.message.reply_to_message:

            if len(context.args) < 2 or not re.match(r"^\d+$", context.args[0]):
                if action == PunishmentType.BAN:
                    return await Warnings.how_to_use_ban(update)
                else:
                    return await Warnings.how_to_use_unban(update)

            reason = " ".join(context.args[1:])
            user_id = context.args[0]
            try:
                user = await context.bot.get_chat(user_id)
                username = f"@{user.username}" if user.username else f"user_{user_id}"
            except Exception as e:
                logging.warning(
                    f"Не удалось получить информацию о пользователе {user_id}: {e}"
                )
                username = f"user_{user_id}"

        else:
            if len(context.args) < 1:
                if action == PunishmentType.BAN:
                    return await Warnings.how_to_use_ban(update)
                else:
                    return await Warnings.how_to_use_unban(update)

            target_user = update.message.reply_to_message.from_user
            user_id = target_user.id
            username = (
                f"@{target_user.username}"
                if target_user.username
                else f"user_{user_id}"
            )
            reason = " ".join(context.args)

        if self.verify.is_bot(user_id):
            return await update.message.reply_text(
                f"❌ Невозможно применить данную команду к боту!"
            )

        result = repo.get(user_id)

        if result is not None:
            await update.message.reply_text(f"❌ Пользователь уже {word}.")
            return

        if self.verify.is_admin(
            update.effective_user.id, 2
        ) or await self.verify.is_owner(update):
            report_text = ""

            if self.verify._is_has_try_pynishment(user_id, action):
                result = jun_repo.get_jun(user_id)
                report_text += f"✅ Вы подтвердили запрос на {prefix}бан от младшего администратора {result[3]}, созданный {result[6]}.\n\n"
                reason += f", {result[4]}"
                jun_repo.remove_jun(user_id)

            agreed_chats, failed_chats = await self._command(
                context, action, user_id, username
            )

            status_msg = await update.message.reply_text(
                f"🔄 Начинаю {prefix}бан {username} во всех чатах..."
            )

            if old_admin_user:
                admin_user += f", {old_admin_user}"

            report_text += (
                f"• Пользователь {username} {word}.\n"
                f"• Причина: {reason}\n"
                f"• Администратор(ы): {admin_user}\n"
                f"✅ Успешно в {len(agreed_chats)} чатах."
            )

            if action == PunishmentType.UNBAN:
                self.unban_repo.delete("user_id", user_id)

            if failed_chats:
                report_text += f"\n❌ Ошибки в {len(failed_chats)} чатах."

            data = {
                "user_id": user_id,
                "username": username,
                "reason": reason,
                "admin_user": admin_user,
            }

            repo.append(data)

            await status_msg.edit_text(report_text)

        elif self.verify.is_admin(update.effective_user.id, 1):

            if self.verify._is_has_try_pynishment(user_id, action):

                if self.verify._is_already_try(admin_id, action):
                    await update.message.reply_text(
                        f"• Вы уже запросили {prefix}бан. Попросите другого администратора подтвердить его. /admins"
                    )
                    return

                agreed_chats, failed_chats = await self._command(
                    context, action, user_id, username
                )

                status_msg = await update.message.reply_text(
                    f"🔄 Начинаю {prefix}бан {username} во всех чатах..."
                )

                result = jun_repo.get_jun(user_id)

                reason += f", {result[3]}"

                report_text = (
                    f"• Вы, {admin_user}, подтвердили {prefix}бан от младшего администратора {result[3]}, созданную {result[6]}.\n"
                    f"• Нарушитель: {username}\n"
                    f"• Причина: {reason}\n"
                    f"✅ Успешно в {len(agreed_chats)} чатах."
                )

                if action == PunishmentType.UNBAN:
                    self.unban_repo.delete("user_id", user_id)

                jun_repo.remove_jun(user_id)

                admin_user += f" ,{result[4]}"

                if failed_chats:
                    report_text += f"\n❌ Ошибки в {len(failed_chats)} чатах."

                data = {
                    "user_id": user_id,
                    "username": username,
                    "reason": reason,
                    "admin_user": admin_user,
                }

                repo.append(data)

            else:

                data = {
                    "user_id": user_id,
                    "username": username,
                    "admin_user": admin_user,
                    "reason": reason,
                    "admin_id": admin_id,
                }

                jun_repo.append_jun(data)

                await update.message.reply_text(
                    f"✅ Вы успешно подали заявку на {prefix}бан {username}.\n"
                    "• Попросите другого администратора подтвердить её. /admins\n"
                    f"• Причина: {reason}"
                )
                return

        else:
            return await Warnings.not_admin(update)

    async def ban(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.blacklist(update, context, PunishmentType.BAN)

    async def unban(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.blacklist(update, context, PunishmentType.UNBAN)

    def _get_repo_and_prefix(self, action: PunishmentType):
        if action == PunishmentType.BAN:
            return self.ban_repo, self.jun_ban_repo, "", "забанен"
        else:
            return self.unban_repo, self.jun_unban_repo, "раз", "разбанен"
