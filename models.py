from dataclasses import dataclass


@dataclass
class Account:
    login_tg: str
    id_tg: str | None
    is_active: bool = True
    is_onboarded: bool = True
    is_test_finished: bool = True
    has_pd: bool = True
