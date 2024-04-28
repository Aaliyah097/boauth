import os
from aiogram.types import InlineKeyboardButton, KeyboardButton, WebAppInfo, KeyboardButtonRequestUser
import vars


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
            request_id=request_id,
        )
    )


def MainMenuButton():
    return KeyboardButton(text=vars.MAIN_MENU_BUTTON)


def FamousFriendButton():
    return KeyboardButton(text=vars.FAMOUES_FRIEND_BUTTON)
