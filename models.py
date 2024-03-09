from dataclasses import dataclass


@dataclass
class Account:
    pk: int
    login_tg: str
    id_tg: str | None
    is_active: bool
