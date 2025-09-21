from bot_module.repositories.class_ban_log_repository import BanLogRepository
from bot_module.repositories.class_unban_log_repository import UnbanLogRepository
from bot_module.class_enum import PunishmentType
from bot_module.class_warnings import Warnings
from bot_module.class_verify import Verify
from telegram import Update
from telegram.ext import ContextTypes
import re
import logging

class ShowBlacklist:

    def __init__(
        self, 
        ban_repo: BanLogRepository,
        unban_repo: UnbanLogRepository,
        verify: Verify
    ):
        self.ban_repo = ban_repo
        self.unban_repo = unban_repo
        self.verify = verify

    async def demonstrate(
            self, 
            update: Update, 
            context: ContextTypes.DEFAULT_TYPE,
            action: PunishmentType
    ):
        
        if not self.verify.is_admin(
            update.effective_user.id, 1
        ) or not await self.verify.is_owner(update):
            return await Warnings.not_admin(update)
        
        try:
            page = int(context.args[0]) if context.args and context.args[0].isdigit() else 1
        except (IndexError, ValueError):
            page = 1

        repo, prefix = self._get_repo_and_prefix(action)
        data = repo.get_all_punishments()

        items_per_page = 5
        total_pages = (len(data) + items_per_page - 1) // items_per_page
        
        start_idx = (page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, len(data))
        page_data = data[start_idx:end_idx]

        report_text = f"📄 Лог {prefix}баненных пользователей (страница {page}/{total_pages}):\n\n"

        if not data:
            await update.message.reply_text(f"📄 Список {prefix}баненных пользователей пуст.")
            return

        if page < 1 or page > total_pages:
            await update.message.reply_text(f"❌ Страница {page} не существует. Доступно страниц: {total_pages}.")
            return

        for i, info in enumerate(page_data, start=start_idx + 1):

            report_text += (
                f'{i}. Пользователь {info[2]} (ID: {info[1]})\n'
                f"   Причина: {info[3]}\n"
                f"   Забанил: {info[4]}\n"
                f"   Время операции: {info[5]}\n\n"
            )

        report_text += '• Для выбора другой страницы укажите ее цифру/число первым аргументом команды.'

        await update.message.reply_text(report_text)
        return

    def _get_repo_and_prefix(self, action: PunishmentType):
            if action == PunishmentType.BAN:
                return self.ban_repo, 'за'
            else:
                return self.unban_repo, 'раз'
            
    async def ban(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.demonstrate(update, context, PunishmentType.BAN)

    async def unban(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.demonstrate(update, context, PunishmentType.UNBAN)