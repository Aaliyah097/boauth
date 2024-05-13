from dataclasses import dataclass
from src.cache import RedisConnector


class Account:
    def __init__(self,
                 login_tg: str,
                 id_tg: str,
                 is_onboarded: bool,
                 birthday: str | None,
                 values: list,
                 vocabulary_category: int | None
                 ):
        self.login_tg: str = login_tg
        self.id_tg: str = id_tg
        self.is_onboarded: bool = is_onboarded
        self.birthday: str | None = birthday
        self.values: list = values or []
        self.vocabulary_category: int | None = vocabulary_category

        self.partial_signup: bool = False

        if bool(self.birthday) and bool(self.values):
            self.partial_signup: bool = True

        self.full_signup: bool = False

        if bool(self.birthday) and bool(self.values) and bool(self.vocabulary_category):
            self.full_signup = True

    def serilize(self) -> dict:
        return {
            'login_tg': self.login_tg or '',
            'id_tg': self.id_tg or '',
            'is_onboarded': self.is_onboarded or False,
            'birthday': self.birthday or '',
            'values': self.values or '',
            'vocabulary_category': self.vocabulary_category or 0,
        }

    @staticmethod
    def deserialize(payload: dict) -> 'Account':
        return Account(
            login_tg=payload.get('login_tg'),
            id_tg=payload.get('id_tg'),
            is_onboarded=payload.get('is_onboarded'),
            birthday=payload.get('birthday'),
            values=payload.get('values'),
            vocabulary_category=payload.get('vocabulary_category'),
        )


class StarProfile:
    def __init__(self,
                 id_tg: int,
                 photo: str,
                 gender: str,
                 name: str):
        self.id_tg: int = id_tg or 0
        self.photo: str = photo or ""
        self.gender: str = gender or ""
        self.name: str = name or ""

    def serialize(self) -> dict:
        return {
            'id_tg': self.id_tg or '',
            'photo': self.photo or '',
            'gender': self.gender or '',
            'name': self.name or ''
        }

    @staticmethod
    def deserialize(payload: dict) -> 'StarProfile':
        return StarProfile(
            id_tg=payload.get('id_tg'),
            photo=payload.get("photo"),
            gender=payload.get("gander"),
            name=payload.get("name")
        )


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
