# t.me/regbo_bot
import os
from dotenv import load_dotenv
import aiogram.exceptions
from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, InlineKeyboardButton, ReplyKeyboardMarkup, WebAppInfo, KeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from utils import (
    get_start_params,
    get_signup_redirect_url,
    verify_login,
    make_nonce,
    store_telegram_id,
    is_valid_url
)
from api_requests import get_account, activate_account, signup_user
from exceptions import UserNotFoundError
import vars


load_dotenv(".env")
router = Router()


@router.message(Command("health"))
async def check_health(msg: Message):
    await msg.reply("OK")


@router.message(Command("friend"))
async def calc_friendship(msg: Message, command: CommandObject):
    login, first_name, telegram_id = msg.from_user.username, msg.from_user.first_name, str(msg.from_user.id)

    nonce = await store_telegram_id(make_nonce(), telegram_id)

    await msg.answer(
        vars.ONBOARDING_REQUIRED, 
        parse_mode=ParseMode.HTML, 
        reply_markup=InlineKeyboardMarkup(
            row_width=1,
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='Завершить регистрацию', 
                        web_app=WebAppInfo(
                                url=os.environ.get("WEB_ONBOARDING_REDIRECT_URL", "%s") % nonce
                            )
                        )
                ]
            ])
        )

    # TODO предложить выбрать друга из списка
    # TODO рассчитаь коэф дружбы



@router.message(Command("start"))
async def start_handler(msg: Message, command: CommandObject):
    login, first_name, telegram_id = msg.from_user.username, msg.from_user.first_name, str(msg.from_user.id)

    if not login:
        await msg.answer(vars.LOGIN_NOT_FOUND_MESSAGE, parse_mode=ParseMode.HTML)
        return

    # Проверяем есть ли такой ТГ_ИД у нас в базе
    try:
        account = await get_account(verify_login(login))
    except UserNotFoundError:
        account = await signup_user(login, telegram_id)

    # формируем одноразовый код
    nonce = await store_telegram_id(make_nonce(), telegram_id)

    if command.args:
        # отправляем назад в приложение
        redirect_url = os.environ.get("MOBILE_REDIRECT_URI", "%s") if command.args == 'mobile' else os.environ.get("WEB_REDIRECT_URI", "%s")
        message = vars.AUTH_SUCCESS % (str(first_name), str(nonce))
    else:
        # отправляем в вебап
        redirect_url = os.environ.get("WEB_ONBOARDING_REDIRECT_URL", "%s")
        message = vars.ONBOARDING_REQUIRED % (str(first_name), str(nonce))

    if "?nonce=" not in redirect_url:
        redirect_url += f"?nonce=%s"
        
    redirect_url = redirect_url % str(nonce)

    if command.args:
        # одноразовый код + ссылка на приложение
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(
                text="Вернуться в приложение", url=str(redirect_url)
            )
        )
        await msg.answer(
            message,
            reply_markup=builder.as_markup() if builder else None,
            parse_mode=ParseMode.HTML
        )
    else:
        # одноразовый код + ссылка на ВЕБАП
        await msg.answer(
            message, 
            parse_mode=ParseMode.HTML, 
            reply_markup=InlineKeyboardMarkup(
                row_width=1,
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text='Завершить регистрацию', 
                            web_app=WebAppInfo(
                                    url=os.environ.get("WEB_ONBOARDING_REDIRECT_URL", "%s") % nonce
                                )
                            )
                    ]
                ]
            )
        )
