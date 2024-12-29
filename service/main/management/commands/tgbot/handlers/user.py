import os

import django
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InputMediaPhoto

from main.management.commands.tgbot.factory.menu import MenuCbData, MenuActions
from main.management.commands.tgbot.handlers.method import checking_existing_user, show_navigation, get_or_create_user, \
    notify_user_referrer
from main.management.commands.tgbot.keyboards.inline import continue_keyboard, age_verification_keyboard, \
    accept_agreement_keyboard, beginning_keyboard, support_keyboard
from main.management.commands.tgbot.keyboards.profile_inline import referrals_keyboard
from main.management.commands.tgbot.misc.states import RegistrationSteps

from main.management.commands.tgbot.handlers.method import games_list
from main.management.commands.tgbot.keyboards.games_inline import build_products_kb

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'diamond.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

from main.models import TelegramUser

user_router = Router()


@user_router.message(CommandStart())
async def user_start(message: Message, bot: Bot, state: FSMContext):
        start_command = message.text
        user_id = message.from_user.id
        referrer_id = str(start_command[7:]) if len(start_command) > 7 else None

        bot_info = await message.bot.get_me()
        bot_username = bot_info.username

        # Формирование ссылки с динамическим именем бота
        referral_link = f"https://t.me/{bot_username}?start={message.from_user.id}"
        share_text = f"Привет! 🎉 Я зарегистрировался в боте и получил бонус! Присоединяйся тоже: {referral_link}"

        if referrer_id and referrer_id == str(user_id):
            await message.answer("🚫 ***Нельзя регистрироваться по своей реферальной ссылке.***\n"
                                 "___Для получения бонусов необходимо пригласить других игроков.___\n", parse_mode="Markdown", reply_markup=referrals_keyboard(share_text))
        else:
            exist = await checking_existing_user(user_id)

            if not exist:
                await message.answer(
                    "Приветствуем вас в нашем игровом боте! 🎲\n"
                    "Чтобы пользоваться, необходимо продолжить",
                    reply_markup=continue_keyboard()
                )
                if referrer_id:
                    await state.update_data(referrer_id=referrer_id)
                    await state.set_state(RegistrationSteps.check_subscription)
            else:
                await show_navigation(message)


@user_router.callback_query(lambda c: c.data == 'continue_action')
async def process_continue_action(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        "Пожалуйста, подтвердите, что вам больше 18 лет, чтобы продолжить.",
        reply_markup=age_verification_keyboard()
    )

@user_router.callback_query(lambda c: c.data == 'age_yes')
async def process_age_verification_yes(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        "___Перед началом игры ознакомьтесь с правилами и подтвердите свое согласие с ними.___\n\n"
        "⚠️ Обязательно прочитайте [правила и условия](https://telegra.ph/Pravila-i-usloviya-ispolzovaniya-servisa-11-19-2/)\n\n"
        "***Вы подтверждаете, что понимаете риски, связанные с онлайн развлечениями?***", parse_mode="Markdown",
        reply_markup=accept_agreement_keyboard()
    )


@user_router.callback_query(lambda c: c.data == 'age_no')
async def process_age_verification_no(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        "Извините, но регистрация доступна только пользователям старше 18 лет."
    )

@user_router.callback_query(lambda c: c.data == 'accept_agreement')
async def process_accept_agreement(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    await callback_query.answer("Спасибо за принятие пользовательского соглашения!", show_alert=True)
    user_data = await state.get_data()
    referrer_id = user_data.get("referrer_id")

    user, created = await get_or_create_user(
        callback_query.from_user.id, callback_query.from_user.username,
        referrer_id)

    if created:
        await notify_user_referrer(referrer_id, callback_query.from_user.username, bot)

    await callback_query.message.edit_text(
        "🎉 Регистрация успешно завершена!\n\n"
        "Добро пожаловать в *Monochrome Project*! 🌟\n\n"
        "Теперь вам доступны все функции нашего бота. Выберите интересующую вас опцию в меню ниже и начните свое путешествие с нами!",
        reply_markup=beginning_keyboard(),
        parse_mode="Markdown"
    )

@user_router.callback_query(lambda c: c.data == 'waiver_agreement')
async def process_waiver_agreement(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    await callback_query.answer("Регистрация была отменена. Не выполнены необходимые условия!", show_alert=True)

@user_router.callback_query(lambda c: c.data == 'main_menu')
async def show_navigation_cmd(message: Message):
    await show_navigation(message)

@user_router.callback_query(MenuCbData.filter(F.action == MenuActions.root))
async def handle_back_button(callback: CallbackQuery):
    await callback.answer()
    await show_navigation(callback)


@user_router.callback_query(MenuCbData.filter(F.action == MenuActions.support))
async def request_support(callback_query: CallbackQuery):
    await callback_query.message.edit_media(media=InputMediaPhoto(media="https://placehold.co/680x240/png/?text=Техническая+поддержка", caption=
        f" Чем вам помочь? Вы можете задать вопрос или сообщить о проблеме.\n\n"
        f"Напишите свой вопрос, и оператор скоро с вами свяжется!"),
        reply_markup=support_keyboard()),

@user_router.callback_query(MenuCbData.filter(F.action == MenuActions.mini_games))
async def handle_mini_games_button(callback: CallbackQuery):
    await callback.answer()
    games = await games_list()
    await callback.message.edit_media(
    media=InputMediaPhoto(media="https://placehold.co/500x300/png/?text=Мини+игры",
                          caption=f" Выберите игру, в которую хотите сыграть:\n\n"),
    reply_markup=build_products_kb(games))
