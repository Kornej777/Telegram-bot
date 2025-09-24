from bot.repositories.base_repo import BaseRepository

class JuniorUnbanRepository(BaseRepository):

    def __init__(self):
        super().__init__("admin_junior_try_unban_log")

    def remove_jun(self, user_id: int) -> bool:
        return self.delete("user_id", user_id)

    def get_jun(self, user_id: int) -> any:
        return self.get_by_field("user_id", user_id)
    
    def get_jun_admin(self, admin_id: int):
        return self.get_by_field('admin_id', admin_id)

    def append_jun(self, data: dict) -> bool:
        return self.add(data)
    
    def get_all_juns(self):
        return self.get_all()
    
    def delete_all_juns(self):
        return self.delete_all()