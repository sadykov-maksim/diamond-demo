import asyncio
import random

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message, InputMediaPhoto

from main.management.commands.tgbot.handlers.method import save_game_history
from main.management.commands.tgbot.misc.states import Form
from main.models import TelegramUser, GameHistory

SLOT_SYMBOLS = ["🍒", "🍋", "🍊", "🍉", "⭐", "💎"]

router = Router()


@router.message(Form.state_1, F.text)
async def handle_slots_bet(message: Message, state: FSMContext):
    bet_amount = message.text

    if bet_amount.isdigit():
        bet_amount = int(bet_amount)
        telegram_user = await TelegramUser.objects.filter(telegram_id=message.from_user.id).afirst()
        if not telegram_user:
            await message.answer("Пользователь не найден.")
            return

        if bet_amount > 0 and telegram_user.balance >= bet_amount:
            telegram_user.balance -= bet_amount
            await telegram_user.asave()

            # Имитируем вращение слотов с заменой сообщений
            await animate_slots(message)

            # Определяем результат игры
            result = [random.choice(SLOT_SYMBOLS) for _ in range(3)]
            win_amount = calculate_slots_payout(result, bet_amount)
            if win_amount > 0:
                telegram_user.balance += win_amount
                result_text = f"Поздравляем! Вы выиграли {win_amount}₽ 🎉"
                outcome = "Победа"
            else:
                result_text = "Увы, вы ничего не выиграли. Попробуйте снова!"
                outcome = "Проигрыш"

            await telegram_user.asave()
            # Сохраняем историю игры
            await save_game_history(telegram_user, "Слоты 🎰", bet_amount, win_amount, outcome)

            await message.answer(
                f"🎰 Ваш результат: {' | '.join(result)} 🎰\n{result_text}\n"
                f"Ваш баланс: {telegram_user.balance}₽\nЧтобы попробовать снова, введите ставку или используйте /start для выхода."
            )
        else:
            await message.answer("Недостаточно средств для ставки. Пополните баланс.")
    else:
        await message.answer("Недопустимая ставка. Пожалуйста, введите сумму ставки в числовом формате.")


async def animate_slots(message: Message):
    """
    Создает эффект анимации вращения слотов.
    """
    animation_steps = 10  # Количество шагов анимации
    previous_message = None  # Переменная для хранения сообщения
    result = []

    for _ in range(animation_steps):
        spin_result = [random.choice(SLOT_SYMBOLS) for _ in range(3)]

        # Удаление предыдущего сообщения, если оно существует
        if previous_message:
            await previous_message.delete()

        # Отправка нового "кадра" анимации
        previous_message = await message.answer(f"🎰 {' | '.join(spin_result)} 🎰")
        await asyncio.sleep(0.3)  # Задержка между кадрами анимации

        # Сохраняем последний результат для окончательного отображения
        result = spin_result

    return result

def calculate_slots_payout(result, bet_amount):
    if result.count(result[0]) == 3:
        return bet_amount * 10
    elif result.count(result[0]) == 2 or result.count(result[1]) == 2:
        return bet_amount * 2
    else:
        return 0
