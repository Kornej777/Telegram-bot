from bot_module import *
from bot_module.class_punishment import Punishment
from telegram.ext import Application, CommandHandler
import logging

class Main:

    @staticmethod
    def run():

        verify = Verify()

        if not verify.bot_token():
            logging.error("❌ BOT_TOKEN не найден! Проверьте файл .env")

        application = Application.builder().token(verify.bot_token()).build()

        chats_repo = ChatsRepository()
        rangs_repo = RangsRepository()
        ban_repo = BanLogRepository()
        unban_repo = UnbanLogRepository()
        jun_ban_repo = JuniorBanRepository()
        jun_unban_repo = JuniorUnbanRepository()
        show_blacklist = ShowBlacklist(ban_repo, unban_repo, verify)
        admin = Admin(verify, rangs_repo)
        chats = Chats(verify, chats_repo, application.bot)
        punishment = Punishment(
            verify, 
            chats_repo,
            ban_repo,
            unban_repo,
            jun_ban_repo,
            jun_unban_repo
        )

        Tables.init_rangs()
        Tables.debug_database_info()

        data = {
                'user_id': 5592317446,
                'username': '@kornej7',
                'rang': '3'
        }
        rangs_repo.add_rang(data)

        application.add_handler(CommandHandler("t_add_admin", admin.add))
        application.add_handler(CommandHandler("t_remove_admin", admin.remove))
        application.add_handler(CommandHandler("t_admins", admin.list))
        application.add_handler(CommandHandler("t_add_chat", chats.add))
        application.add_handler(CommandHandler("t_remove_chat", chats.remove))
        application.add_handler(CommandHandler("t_chats", chats.list))
        application.add_handler(CommandHandler("t_chats", chats.list))
        application.add_handler(CommandHandler("t_ban", punishment.ban))
        application.add_handler(CommandHandler("t_unban", punishment.unban))
        application.add_handler(CommandHandler("t_ban_log", show_blacklist.ban))
        application.add_handler(CommandHandler("t_unban_log", show_blacklist.unban))

        print("Бот запущен...")
        application.run_polling()

if __name__ == "__main__":
    Main.run()