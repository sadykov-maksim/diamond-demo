from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, InputMediaPhoto, Message
from pydantic import ValidationError

from main.management.commands.tgbot.keyboards.inline import navigation_keyboard, promo_keyboard
from main.models import TelegramUser, Banner
from support.models import SupportTicket, FAQ

from main.models import Game


async def checking_existing_user(user_id: int):
    """
    Асинхронная функция для получения или создания пользователя в базе данных.

    Параметры:
        user_id (int): Telegram ID пользователя.

    Возвращает:
        Tuple[TelegramUser, bool]: Кортеж, содержащий объект пользователя и флаг, указывающий, был ли пользователь создан.
    """
    return TelegramUser.objects.filter(
        telegram_id=user_id,
    ).exists()

async def show_navigation(chat_input):
    """
    Асинхронная функция для отображения главного меню пользователю.

    Эта функция отправляет фотографию с главным меню и прикрепляет клавиатуру навигации
    в ответ на сообщение или на нажатие кнопки.

    Параметры:
        chat_input (Union[CallbackQuery, Message]): Объект, который может быть либо CallbackQuery,
        либо Message, представляющий взаимодействие пользователя.

    Возвращает:
        None: Функция не возвращает значения, но отправляет сообщение пользователю.
    """
    banner = Banner.objects.filter(level=1).first()
    if isinstance(chat_input, CallbackQuery):
        await chat_input.message.edit_media(
            media=InputMediaPhoto(media=banner.file_id,
                                  caption="⚡️Monochrome - «Играй. Выигрывай. Повторяй!» 🎮✨\n"
                                            "🔥 Еженедельные челленджи"),
            reply_markup=navigation_keyboard()
        )
        await chat_input.answer()  # Acknowledge the callback
    elif isinstance(chat_input, Message):

        await chat_input.answer_photo(
            photo=banner.file_id,
            caption="⚡️Monochrome - «Играй. Выигрывай. Повторяй!» 🎮✨\n"
                    "🔥 Еженедельные челленджи",
            reply_markup=navigation_keyboard()
        )

async def show_promo(chat_input):
    """
    Асинхронная функция для отображения главного меню пользователю.

    Эта функция отправляет фотографию с главным меню и прикрепляет клавиатуру навигации
    в ответ на сообщение или на нажатие кнопки.

    Параметры:
        chat_input (Union[CallbackQuery, Message]): Объект, который может быть либо CallbackQuery,
        либо Message, представляющий взаимодействие пользователя.

    Возвращает:
        None: Функция не возвращает значения, но отправляет сообщение пользователю.
    """
    if isinstance(chat_input, CallbackQuery):
        await chat_input.message.edit_media(
            media=InputMediaPhoto(media="https://placehold.co/500x300/png/?text=Неверный промокод", caption="Неверный промокод (media)"),
        )
        await chat_input.answer()  # Acknowledge the callback
    elif isinstance(chat_input, Message):
        await chat_input.answer(text=
            "😕 Упс! Кажется, такого промокода не существует.\n\n"
            "✨ Не расстраивайтесь! Следите за нашими новостями — скоро появятся новые промокоды и бонусы.",
            parse_mode="HTML", reply_markup=promo_keyboard()
        )

async def get_or_create_user(user_id: int, username: str, chat_id: int, referrer_id: str = None):
    """
    Асинхронная функция для получения или создания пользователя в базе данных.

    Параметры:
        user_id (int): Telegram ID пользователя.
        username (str): Имя пользователя в Telegram.
        referrer_id (str, optional): Telegram ID реферера, если указан.

    Возвращает:
        Tuple[TelegramUser, bool]: Кортеж, содержащий объект пользователя и флаг, указывающий, был ли пользователь создан.
    """
    return await TelegramUser.objects.aget_or_create(
        telegram_id=user_id,
        defaults={
            'username': username,
            'referer': referrer_id if referrer_id else None,
        }
    )

async def get_user_tg(user_id: int):
    """
    Асинхронная функция для получения или создания пользователя в базе данных.

    Параметры:
        user_id (int): Telegram ID пользователя.
        username (str): Имя пользователя в Telegram.
        referrer_id (str, optional): Telegram ID реферера, если указан.

    Возвращает:
        Tuple[TelegramUser, bool]: Кортеж, содержащий объект пользователя и флаг, указывающий, был ли пользователь создан.
    """
    user_id = TelegramUser.objects.filter(telegram_id=user_id).first()
    return user_id


async def notify_user_referrer(referrer_id: str, username: str, bot: Bot):
    try:
        await bot.send_message(
            referrer_id,
            f"По вашей ссылке зарегистрировался новый пользователь\nВаш друг: @{username}"
        )
    except Exception:
        pass

async def get_avatar(bot, user_id):
    try:
        user_photos = await bot.get_user_profile_photos(user_id, limit=1)
        if user_photos.photos:
            return user_photos.photos[0][-1].file_id
        else:
            raise ValueError("Аватар отсутствует")
    except (TelegramBadRequest, ValueError):
        # Загружаем аватар по умолчанию при ошибке
        return 'AgACAgIAAxkBAAIDtGcfs6JJWnyzeXQzrtHYvTxYtzGUAAKo6DEbOxoAAUmsjpAeViz_kAEAAwIAA3gAAzYE'


async def get_user_balance(user_id: int):
    """
    Асинхронная функция для получения баланса пользователя по его Telegram ID.

    Параметры:
        user_id (int): Telegram ID пользователя.

    Возвращает:
        float: Текущий баланс пользователя.
    """
    account = TelegramUser.objects.filter(telegram_id=user_id).first()
    return account.balance

async def get_faq():
    """
    Асинхронная функция для получения баланса пользователя по его Telegram ID.

    Параметры:
        user_id (int): Telegram ID пользователя.

    Возвращает:
        float: Текущий баланс пользователя.
    """
    faq = FAQ.objects.filter(is_active=True)
    return faq

async def get_answer_for_faq(callback_data: str):
    """
    Асинхронная функция для получения баланса пользователя по его Telegram ID.

    Параметры:
        user_id (int): Telegram ID пользователя.

    Возвращает:
        float: Текущий баланс пользователя.
    """

    try:
        faq = FAQ.objects.get(callback_data=callback_data)
        return faq
    except (IndexError, ValueError, FAQ.DoesNotExist):
        return "Ответ на этот вопрос не найден."

async def create_support_ticket( ticket_type, user, description):
    telegram = await get_user_tg(user)
    description = str(description)

    try:
        ticket = SupportTicket.create_ticket(user, ticket_type, description)
        return f"Номер обращения: {ticket.id}\nСпасибо за сообщение! Мы скоро разберёмся с вашей проблемой. 🛠️"
    except ValidationError as e:
        print(f"Ошибка при создании тикета: {e}")

async def games_list():
    try:
        games = Game.objects.filter(is_active=True)
        return games
    except Game.DoesNotExist as e:
        print(e.message)