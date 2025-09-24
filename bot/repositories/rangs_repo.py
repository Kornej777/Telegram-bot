from bot.tables import DB_PATH
from bot.repositories.base_repo import BaseRepository


class RangsRepository(BaseRepository):

    def __init__(self):
        super().__init__("rangs")

    def delete_user(self, user_id: int) -> bool:
        return self.delete("user_id", user_id)

    def get_user(self, user_id: int) -> any:
        return self.get_by_field("user_id", user_id)

    def add_rang(self, data: dict) -> bool:
        return self.add(data)
    
    def get_all_rangs(self):
        return self.get_all()
