import os
import random
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardButton, KeyboardButton, WebAppInfo, KeyboardButtonRequestUser
from src import vars


def BackToAppButton(redirect_url: str):
    return InlineKeyboardButton(text=vars.BACK_TO_APP_BUTTON, url=str(redirect_url))


def SignupFinishButton(nonce: str):
    return KeyboardButton(
        text=vars.SIGNUP_FINISHED_REQUIRED_BUTTON,
        web_app=WebAppInfo(
            url=os.environ.get("WEB_ONBOARDING_REDIRECT_URL", "%s") % str(nonce))
    )


def SelectFriendButton(request_id: int):
    return KeyboardButton(
        text=vars.SELECT_FRIEND_BUTTON,
        request_user=KeyboardButtonRequestUser(
            request_id=request_id or random.randint(1, 999999),
        )
    )


def MainMenuButton():
    return KeyboardButton(text=vars.MAIN_MENU_BUTTON)


def FamousFriendButton():
    return KeyboardButton(text=vars.FAMOUES_FRIEND_BUTTON)


def ProductionButton():
    return KeyboardButton(text=vars.PRODUCTION_STATUS)


def Menu(telegram_id) -> ReplyKeyboardBuilder:
    buttons_pack = [
        SelectFriendButton(telegram_id),
        FamousFriendButton(),
        ProductionButton()
    ]
    builder = ReplyKeyboardBuilder()
    for button in buttons_pack:
        builder.row(button)

    return builder
