from random import random
import asyncio
import random

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message, InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from main.management.commands.tgbot.handlers.games.factory import GameCbData, GameActions
from main.management.commands.tgbot.misc.states import Chests
from main.models import TelegramUser

router = Router()
# Настройки уровней
LEVELS = {
    1: {"buttons_count": 3, "winning_buttons": 1},
    2: {"buttons_count": 4, "winning_buttons": 1},
    3: {"buttons_count": 5, "winning_buttons": 1},
    4: {"buttons_count": 6, "winning_buttons": 1},
    5: {"buttons_count": 6, "winning_buttons": 2},
}

# Генерация кнопок и выигрышных
def generate_buttons(level):
    config = LEVELS[level]
    buttons = [f"Кнопка {i + 1}" for i in range(config["buttons_count"])]
    winning_buttons = random.sample(buttons, config["winning_buttons"])  # Выбираем N выигрышных
    return buttons, winning_buttons
@router.callback_query(Chests.state_1, lambda c: c.data == 'place_bet')
async def start_game(call: CallbackQuery, state: FSMContext):
    # Устанавливаем начальный уровень
    current_level = 1
    await state.update_data(level=current_level)

    # Получаем пользователя из базы данных
    user = TelegramUser.objects.filter(telegram_id=call.from_user.id).first()
    if not user:
        await call.answer("Ошибка: Пользователь не найден.", show_alert=True)
        return

    # Устанавливаем ставку
    bet_amount = 1000  # Пример суммы ставки
    if user.balance < bet_amount:
        await call.answer("Недостаточно средств на балансе для ставки.", show_alert=True)
        return

    # Вычитаем ставку из баланса
    user.balance -= bet_amount
    user.save()

    # Сохраняем ставку в состоянии
    await state.update_data(bet_amount=bet_amount)

    # Переходим к отправке уровня
    await send_level(call, state)
async def send_level(call: CallbackQuery, state: FSMContext):
    # Получаем текущий уровень
    user_data = await state.get_data()
    current_level = user_data.get("level", 1)
    bet_amount = user_data.get("bet_amount", 0)

    # Генерируем кнопки для текущего уровня
    buttons, winning_buttons = generate_buttons(current_level)
    await state.update_data(winning_buttons=winning_buttons)

    # Получаем пользователя и его баланс
    user = TelegramUser.objects.filter(telegram_id=call.from_user.id).first()

    # Создаем inline клавиатуру
    builder = InlineKeyboardBuilder()
    for button in buttons:
        builder.row(InlineKeyboardButton(
            text=button,
            callback_data=f"choice:{button}")
        )
    builder.adjust(3)

    # Отправляем сообщение
    await call.message.edit_media(
        media=InputMediaPhoto(
            media=f"https://placehold.co/500x300/png/?text=Уровень {current_level}",
            caption=f"Уровень {current_level}: Выберите кнопку\n"
                    f"Ваш баланс: {user.balance}\n"
                    f"Ставка: {bet_amount}",
        ),
        reply_markup=builder.as_markup()
    )

@router.callback_query(lambda c: c.data.startswith("choice:"))
async def handle_choice(call: CallbackQuery, state: FSMContext):
    # Получаем данные состояния
    user_data = await state.get_data()
    winning_buttons = user_data.get("winning_buttons", [])
    current_level = user_data.get("level", 1)

    # Получаем выбор пользователя
    selected_button = call.data.split(":")[1]

    if selected_button in winning_buttons:
        # Если выигрышная кнопка
        if current_level == 5:
            # Если это финальный уровень
            await call.message.edit_caption(
                caption=f"Поздравляем! Вы прошли игру! Вы выбрали {selected_button}, и это выигрышная кнопка!",
                reply_markup=None
            )
            await state.clear()
        else:
            # Переход на следующий уровень
            await state.update_data(level=current_level + 1)
            await call.answer(
                text=f"Поздравляем! Вы выбрали {selected_button}, и это выигрышная кнопка! Переход на уровень {current_level + 1}...",
                show_alert=True,
            )
            await send_level(call, state)
    else:
        # Проигрыш
        buttons = [
            [
                InlineKeyboardButton(text="🔄 Пробовать снова", callback_data=GameCbData(action=GameActions.text,  id=1,
                title="Сундунки",
                code="chests",
                min_bet=1000).pack()),
            ],
            [
                InlineKeyboardButton(text="📋 Перейти в меню", callback_data="main_menu"),
            ]
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        await call.message.edit_caption(
            caption="Вы проиграли. Попробуйте снова!",
            reply_markup=keyboard
        )
        await state.clear()