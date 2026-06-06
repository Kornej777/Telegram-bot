from bot.warnings import Warnings
from bot.verify import Verify
from bot.repositories.junior_ban_repo import JuniorBanRepository
from bot.repositories.junior_unban_repo import JuniorUnbanRepository
from telegram import Update
from telegram.ext import ContextTypes

class ShowJuniorRequests:

    def __init__(
            self, 
            verify: Verify,
            junior_ban: JuniorBanRepository,
            junior_unban: JuniorUnbanRepository
    ):
        self.verify = verify
        self.junior_ban = junior_ban
        self.junior_unban = junior_unban

    async def demonstrate(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        
        if not self.verify.is_admin(
            update.effective_user.id, 1
        ) or not await self.verify.is_owner(update):
            return await Warnings.not_admin(update)

        data_ban = self.junior_ban.get_all_juns()
        data_unban = self.junior_unban.get_all_juns()

        report_text = f"📄 Список заявок младших администраторов:\n\n"

        if not data_unban and not data_ban:
            await update.message.reply_text(f"📄 Список заявок пуст.")
            return

        if data_ban:
            report_text += '🔸 Заявки на бан:\n\n'
            for req in data_ban:
                report_text += (
                    f'• Пользователь {req[2]} (ID: {req[1]})\n'
                    f'• Причина: {req[4]}\n'
                    f'• Администратор: {req[3]}\n'
                    f'• Время: {req[6]}\n\n'
                )

        if data_unban:
            report_text += '🔹 Заявки на разбан:\n\n'
            for req in data_unban:
                report_text += (
                    f'• Пользователь {req[2]} (ID: {req[1]})\n'
                    f'• Причина: {req[4]}\n'
                    f'• Администратор: {req[3]}\n'
                    f'• Время: {req[6]}\n\n'
                )

        await update.message.reply_text(report_text)
        return
    
    async def remove_requests(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.verify.is_owner(update):
            return await Warnings.not_admin(update)
        
        quantity_of_ban_requests = len(self.junior_ban.get_all_juns())
        quantity_of_unban_requests = len(self.junior_unban.get_all_juns())
        amount = quantity_of_ban_requests + quantity_of_unban_requests

        self.junior_ban.delete_all_juns()
        self.junior_unban.delete_all_juns()

        await update.message.reply_text(f'✅ Успешно удалено {amount} заявок от младших модераторов.')
        return

