from random import randint
from typing import Literal

from line_bot_server.models import User


class UserManager:
    USER_TYPE = {
        "deleted": -1,
        "user": 0,
        "admin": 1,
    }

    def __init__(self) -> None:
        self._aikotoba = self.generate_aikotoba()

    @property
    def aikotoba(self) -> str:
        return self._aikotoba

    def add_user(self, user_id: int, user_type: Literal["user", "admin"]):
        User.objects.create(user_id=user_id, type=self.USER_TYPE[user_type])

    def is_admin(self, user: User):
        if user.type == self.USER_TYPE["admin"]:
            return True
        else:
            return False

    def is_user(self, user: User):
        if user.type != self.USER_TYPE["deleted"]:
            return True
        else:
            return False

    def authorize(self, aikotoba: str, user_id: int, user_type: Literal["user", "admin"]):
        if aikotoba == self.aikotoba:
            self.add_user(user_id, user_type)
            return True
        else:
            return False

    def generate_aikotoba(self):
        seed = (
            ("きれいな", "かわいい", "眠い", "自立した", "お腹いっぱい", "元気な", "素晴らしい", "大切な"),
            ("うさぎ", "うさちゃん", "ラビット", "ぷりん", "アイドル"),
        )
        indexes = [randint(0, len(s) - 1) for s in seed]
        self._aikotoba = "".join([seed[i][j] for i, j in enumerate(indexes)])
        return self.aikotoba
