from bot.repositories.base_repo import BaseRepository

class ChatsRepository(BaseRepository):

    def __init__(self):
        super().__init__("chats")

    def delete_chat(self, chat_id: int) -> bool:
        return self.delete("chat_id", chat_id)

    def get_chat(self, chat_id: int) -> any:
        return self.get_by_field("chat_id", chat_id)

    def add_chat(self, data: dict) -> bool:
        return self.add(data)
    
    def get_all_chats(self):
        return self.get_all()