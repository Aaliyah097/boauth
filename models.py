from dataclasses import dataclass
from cache import RedisConnector


class Account:
    def __init__(self,
                 login_tg: str,
                 id_tg: str,
                 is_onboarded: bool,
                 birthday: str | None,
                 values: list,
                 vocabulary_category: int | None
                 ):
        login_tg: str = login_tg
        id_tg: str = id_tg
        is_onboarded: bool = is_onboarded
        birthday: str | None = birthday
        values: list = values
        vocabulary_category: int | None = vocabulary_category

        self.partial_signup: bool = False

        if bool(birthday) and bool(values):
            self.partial_signup: bool = True

        self.full_signup: bool = False

        if bool(birthday) and bool(values) and bool(vocabulary_category):
            self.full_signup = True


class Action:
    def __init__(self, tg_id: str):
        self.tg_id = str(tg_id)

    async def get_last(self) -> str | None:
        async with RedisConnector() as connection:
            action = await connection.get(self.tg_id)
            return action.decode('utf-8') if action else None

    async def save_last(self, action: str) -> None:
        async with RedisConnector() as connection:
            return await connection.set(self.tg_id, str(action))
