import sqlite3
import os
from dotenv import load_dotenv
from telegram import Update
from bot.punishment_type import PunishmentType
from bot.tables import DB_PATH
from bot.repositories.rangs_repo import RangsRepository
from bot.repositories.chats_repo import ChatsRepository
from bot.repositories.junior_ban_repo import JuniorBanRepository
from bot.repositories.junior_unban_repo import JuniorUnbanRepository

class Verify:

    def __init__(self, rangs: RangsRepository, chats: ChatsRepository, junior_ban: JuniorBanRepository, junior_unban: JuniorUnbanRepository):
        self.owner = [5592317446]
        self.bot = [7538212205, 7937929115]
        self.rangs = rangs
        self.chats = chats
        self.junior_ban = junior_ban
        self.junior_unban = junior_unban

    def bot_token(self):
        load_dotenv()
        return os.getenv("BOT_TOKEN")

    async def is_owner(self, update: Update):
        user = update.effective_user

        return user and user.id in self.owner

    def is_admin(self, user_id: int, rang=1):

        result = self.rangs.get_user(user_id)

        if result is None:
            return False

        user_rang = int(result[3])

        return user_rang >= rang
    
    def is_bot(self, user_id: int):
        return user_id in self.bot


    def is_chat(self, chat_id):

        result = self.chats.get_chat(chat_id)

        if result is None:
            return False
        else:
            return True

    def can_overwrite_rang(self, user_id, new_rang):

        result = self.rangs.get_user(user_id)

        if result is None:
            return True

        current_rang = int(result[3])
        new_rang_int = int(new_rang)

        return new_rang_int > current_rang


    def _is_has_try_pynishment(self, user_id, action: PunishmentType) -> bool:

        if action == PunishmentType.BAN:
            repo = self.junior_ban
        else:
            repo = self.junior_unban

        result = repo.get_jun(user_id)

        if result:
            return True
        else:
            return False

    def _is_already_try(self, admin_id, action: PunishmentType) -> bool:

        if action == PunishmentType.BAN:
            repo = self.junior_ban
        else:
            repo = self.junior_unban

        result = repo.get_jun_admin(admin_id)

        if result:
            return True
        else:
            return False