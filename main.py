from class_admin import (
    Verify,
    Tables,
    Admin,
    Chats,
    RangsRepository,
    ChatsRepository,
)
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import logging

verify = Verify()

if not verify.bot_token():
    logging.error("❌ BOT_TOKEN не найден! Проверьте файл .env")

application = Application.builder().token(verify.bot_token()).build()

chats_repo = ChatsRepository()
rangs_repo = RangsRepository()
admin = Admin(verify, rangs_repo)
chats = Chats(verify, chats_repo, application.bot)
Tables.debug_database_info()
Tables.init_rangs()

application.add_handler(CommandHandler("t_add_admin", admin.add))
application.add_handler(CommandHandler("t_remove_admin", admin.remove))
application.add_handler(CommandHandler("t_admins", admin.list))
application.add_handler(CommandHandler("t_add_chat", chats.add))
application.add_handler(CommandHandler("t_remove_chat", chats.remove))
application.add_handler(CommandHandler("t_chats", chats.list))


print("Бот запущен...")
application.run_polling()
