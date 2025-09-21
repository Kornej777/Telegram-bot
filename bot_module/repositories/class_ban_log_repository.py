from bot_module.repositories.class_base_repository import BaseRepository

class BanLogRepository(BaseRepository):

    def __init__(self):
        super().__init__("ban_log")

    def remove(self, user_id: int) -> bool:
        return self.delete("user_id", user_id)

    def get(self, user_id: int) -> any:
        return self.get_by_field("user_id", user_id)

    def append(self, data: dict) -> bool:
        return self.add(data)
    
    def get_all_punishments(self):
        return self.get_all()