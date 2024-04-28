# t.me/regbo_bot
from aiogram import F
import os
from enum import Enum
from dotenv import load_dotenv
import aiogram.exceptions
from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import (
    Message,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    WebAppInfo,
    KeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButtonRequestUser,
    InputFile,
    FSInputFile,
    BufferedInputFile
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.enums import ParseMode
from utils import (
    verify_login,
    make_nonce,
    store_telegram_id,
    is_valid_url,
    make_friend_k_picture
)
from api_requests import get_account, activate_account, signup_user, calc_friendship_k
from exceptions import UserNotFoundError, UnknownError
import vars
from models import Action, Account
from buttons import BackToAppButton, SignupFinishButton, SelectFriendButton, MainMenuButton, FamousFriendButton


load_dotenv(".env")
router = Router()


class Actions(str, Enum):
    friend = 'friend'


@router.message(Command("health"))
async def check_health(msg: Message):
    await msg.reply("OK")


@router.message(F.user_shared)
async def on_user_shared(message: Message):
    buttons_pack = [
        SelectFriendButton(message.user_shared.request_id),
        MainMenuButton(),
        FamousFriendButton()
    ]
    builder = ReplyKeyboardBuilder()
    for button in buttons_pack:
        builder.row(button)

    try:
        k = await calc_friendship_k(message.user_shared.request_id,
                                    message.user_shared.user_id)
    except UnknownError as e:
        await message.answer(text=str(e))
        return
    except UserNotFoundError:
        await message.answer_photo(
            FSInputFile('static/user_not_found.jpg'),
            caption=vars.USER_NOT_FOUND % "Твоем друге",
            reply_markup=builder.as_markup(resize_keyboard=True)
        )
        return

    file = await make_friend_k_picture(k)
    file.seek(0)
    await message.answer_photo(
        BufferedInputFile(
            file.read(),
            f'{message.user_shared.request_id}_{message.user_shared.user_id}_k.png'
        ),
        caption=vars.K_FRIENDSHIP_EXPLANATION,
        reply_markup=builder.as_markup(resize_keyboard=True)
    )


async def handle_auth(msg: Message, command: CommandObject):
    telegram_id, username = str(msg.from_user.id), str(
        msg.from_user.first_name or msg.from_user.login)

    nonce = await store_telegram_id(make_nonce(), telegram_id)

    if command.args == 'mobile':
        redirect_url = os.environ.get("MOBILE_REDIRECT_URI", "%s") % str(nonce)
    else:
        redirect_url = os.environ.get("WEB_REDIRECT_URI", "%s") % str(nonce)

    message = vars.AUTH_SUCCESS % (username, str(nonce))
    builder = InlineKeyboardBuilder()
    builder.row(BackToAppButton(str(redirect_url)))

    await msg.answer(
        message,
        reply_markup=builder.as_markup(
            one_time_keyboard=True) if builder else None,
        parse_mode=ParseMode.HTML
    )


async def handle_signup_required(msg: Message):
    telegram_id = str(msg.from_user.id)

    nonce = await store_telegram_id(make_nonce(), telegram_id)

    builder = ReplyKeyboardBuilder()
    builder.row(SignupFinishButton(str(nonce)))

    await msg.answer(
        vars.ONBOARDING_REQUIRED,
        parse_mode=ParseMode.HTML,
        reply_markup=builder.as_markup(resize_keyboard=True),
    )


async def handle_select_friend_request(msg: Message):
    telegram_id, username = str(msg.from_user.id), str(
        msg.from_user.first_name or msg.from_user.login)

    builder = ReplyKeyboardBuilder()
    builder.row(SelectFriendButton(telegram_id))

    await msg.answer(
        vars.SELECT_FRIEND_REQUEST % str(username),
        parse_mode=ParseMode.HTML,
        reply_markup=builder.as_markup(resize_keyboard=True),
    )
    return


@ router.message(Command("start"))
async def handle_start(msg: Message, command: CommandObject):
    login, first_name, telegram_id = msg.from_user.username, msg.from_user.first_name or msg.from_user.username, str(
        msg.from_user.id)

    if not login:
        await msg.answer(vars.LOGIN_NOT_FOUND_MESSAGE, parse_mode=ParseMode.HTML)
        return

    try:
        account = await get_account(verify_login(login))
    except UserNotFoundError:
        account = await signup_user(login, telegram_id)

    if command.args:
        await handle_auth(msg, command)
        return

    if not account.partial_signup:
        await handle_signup_required(msg)
    else:
        await handle_select_friend_request(msg)


@ router.message()
async def handle_message(msg: Message):
    login, first_name, telegram_id = msg.from_user.username, msg.from_user.first_name, str(
        msg.from_user.id)

    if msg.web_app_data:
        builder = ReplyKeyboardBuilder()
        builder.row(SelectFriendButton(telegram_id))
        await msg.answer(
            vars.SELECT_FRIEND_REQUEST % (first_name or login),
            parse_mode=ParseMode.HTML,
            reply_markup=builder.as_markup(resize_keyboard=True),
        )
        return

    await msg.answer(vars.DONT_UNDERSTAND % (first_name or login))
