from telegram import Update

class Warnings:
    @staticmethod
    async def not_admin(update: Update):
        return await update.message.reply_text(
            "❌ У вас нет прав для выполнения этой команды."
        )

    @staticmethod
    async def how_to_use_ban(update: Update):
        return await update.message.reply_text(
            "Использование:\n"
            "/r_ban ID причина \n"
            "ИЛИ \n"
            "Ответом на сообщение /r_ban причина"
        )

    @staticmethod
    async def how_to_use_unban(update: Update):
        return await update.message.reply_text(
            "Использование:\n"
            "/r_unban ID причина \n"
            "ИЛИ \n"
            "Ответом на сообщение /r_unban причина"
        )