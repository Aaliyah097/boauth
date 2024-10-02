# t.me/regbo_bot
import re
import os
import random
from enum import Enum
from dotenv import load_dotenv
import aiogram.exceptions
from aiogram import F, flags
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
from src.utils import (
    verify_login,
    make_nonce,
    store_telegram_id,
    is_valid_url,
    make_friend_k_picture,
    download_photo,
    make_star_k_picture,
    get_id_number,
    get_k_message,
    clean_telegram_id,
    get_checks_left_for_reward,
    add_user_check_for_reward,
    get_checks_message
)
from src.api_requests import (
    get_account,
    activate_account,
    signup_user,
    calc_friendship_k,
    get_stars_accounts,
    list_users
)
from src import exceptions
from src import vars
from src import models
from src import buttons
from bot import bot


load_dotenv(".env")
router = Router()


@router.message(Command("health"))
async def check_health(msg: Message):
    await msg.reply("OK")


@router.message(F.user_shared)
@flags.signup_confirm_required()
async def on_user_shared(message: Message):
    builder = buttons.Menu(message.from_user.id)

    try:
        k, is_new = await calc_friendship_k(message.from_user.id,
                                            message.user_shared.user_id)
    except exceptions.UnknownError as e:
        return await message.answer(text=str(e))
    except exceptions.UserNotFoundError:
        return await message.answer_photo(
            FSInputFile('static/user_not_found.jpg'),
            caption=vars.USER_NOT_FOUND,
            reply_markup=builder.as_markup(resize_keyboard=True)
        )
    try:
        file = await make_friend_k_picture(k)
    except exceptions.UnknownError as e:
        return await message.answer(str(e))

    file.seek(0)

    if is_new:
        checks_for_reward = await add_user_check_for_reward(
            message.from_user.id, message.user_shared.user_id
        )
        checks_message = get_checks_message(
            checks_for_reward, has_changed=True)
    else:
        checks_for_reward = await get_checks_left_for_reward(message.from_user.id)
        checks_message = get_checks_message(
            checks_for_reward, has_changed=False)

    await message.answer_photo(
        BufferedInputFile(
            file.read(),
            f'{message.user_shared.request_id}_{message.user_shared.user_id}_k.png'
        ),
        caption=get_k_message(k) % str(get_id_number(
            message.from_user.id)) + checks_message,
        reply_markup=builder.as_markup(resize_keyboard=True)
    )


async def handle_auth(msg: Message, command: CommandObject):
    nonce = await store_telegram_id(make_nonce(6), msg.from_user.id)

    if command.args == 'mobile':
        redirect_url = os.environ.get("MOBILE_REDIRECT_URI", "%s") % nonce
    else:
        redirect_url = os.environ.get("WEB_REDIRECT_URI", "%s") % nonce

    builder = InlineKeyboardBuilder()
    builder.row(buttons.BackToAppButton(redirect_url))

    await msg.answer(
        vars.AUTH_SUCCESS % nonce,
        reply_markup=builder.as_markup(one_time_keyboard=True),
    )


@flags.signup_confirm_required()
async def handle_select_friend_request(msg: Message):
    builder = ReplyKeyboardBuilder()
    builder.row(buttons.SelectFriendButton(msg.from_user.id))

    await msg.answer(
        vars.SELECT_FRIEND_REQUEST,
        reply_markup=builder.as_markup(resize_keyboard=True),
    )


@router.message(Command("start"))
@flags.signup_confirm_required()
async def handle_start(msg: Message, command: CommandObject):
    if command.args:
        return await handle_auth(msg, command)

    await handle_select_friend_request(msg)


@router.message(Command("id"))
@flags.admin_required()
async def handle_id(msg: Message, command: CommandObject):
    return await msg.answer(str(msg.from_user.id))


@router.message(lambda message: message.text == vars.PRODUCTION_STATUS)
@flags.signup_confirm_required()
async def handle_production_status(message: Message):
    return await message.answer_photo(
        FSInputFile('static/prod_status.jpg'),
        caption=vars.PRODUCTION_STATUS_TEXT,
        reply_markup=buttons.Menu(
            message.from_user.id).as_markup(resize_keyboard=True)
    )


@router.message(lambda message: message.text == vars.FAMOUES_FRIEND_BUTTON)
@flags.signup_confirm_required()
async def handle_famous_friend(message: Message):
    builder = buttons.Menu(message.from_user.id)

    try:
        star = random.choice(await get_stars_accounts())
    except IndexError:
        return await message.answer(text=vars.NO_FAMOUS_FRIENDS_FOUND)

    try:
        file = await make_star_k_picture(
            await (calc_friendship_k(message.from_user.id, star.id_tg))[0],
            star
        )
    except exceptions.UnknownError as e:
        return await message.answer(str(e))
    file.seek(0)

    await message.answer_photo(
        BufferedInputFile(
            file.read(),
            f'{message.from_user.id}_{star.id_tg}_k.png'
        ),
        caption=vars.FAMOUS_FRIEND_K_RESULT % (
            star.name, 'ему' if star.gender == 'm' else 'ей'
        ),
        reply_markup=builder.as_markup(resize_keyboard=True)
    )


@router.message()
@flags.signup_confirm_required()
async def handle_message(msg: Message):
    if not msg.web_app_data:
        return await msg.answer(
            vars.MAIN_MENU_TEXT,
            reply_markup=buttons.Menu(
                msg.from_user.id).as_markup(resize_keyboard=True)
        )

    result = ''.join(re.findall(r'\d+', str(msg.web_app_data.data)))
    if result:
        await clean_telegram_id(result)

    builder = ReplyKeyboardBuilder()
    builder.row(buttons.SelectFriendButton(msg.from_user.id))
    return await msg.answer(
        vars.SELECT_FRIEND_REQUEST,
        reply_markup=builder.as_markup(resize_keyboard=True),
    )
