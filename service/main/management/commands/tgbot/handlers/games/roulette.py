from random import random
import asyncio
import random

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message, InputMediaPhoto

from main.management.commands.tgbot.handlers.method import spin_roulette2, save_game_history
from main.management.commands.tgbot.keyboards.inline import roulette_keyboard
from main.management.commands.tgbot.misc.states import Form, Roulette
from main.models import TelegramUser, GameHistory


roulette_results = [
    "Вы выиграли 100 монет! 🎉",
    "Попробуйте снова. Удача не на вашей стороне! 😞",
    "Поздравляем! Вы выиграли джекпот! 💰",
    "Вы ничего не выиграли... Попробуйте ещё раз! 🔄",
    "Сюрприз! Ваш выигрыш — бесплатный кофе! ☕"
]

router = Router()

@router.callback_query(Roulette.state_1, F.text)
async def handle_slots_bet(callback: CallbackQuery, state: FSMContext):
    bet_amount = callback.text

    if bet_amount.isdigit():
        bet_amount = int(bet_amount)
        telegram_user = await TelegramUser.objects.filter(telegram_id=callback.from_user.id).afirst()
        if not telegram_user:
            await callback.message.answer("Пользователь не найден.")
            return
        await callback.message.edit_media(
            media=InputMediaPhoto(media="https://placehold.co/500x300/png/?text=Выберете режим",
                                  caption=f"Недопустимая ставка. Пожалуйста, введите сумму ставки в числовом формате"),
            reply_markup=roulette_keyboard())
    else:
        await callback.answer("Недопустимая ставка. Пожалуйста, введите сумму ставки в числовом формате.")

@router.callback_query(lambda c: c.data == 'spin_roulette')
async def spin_roulette(callback: CallbackQuery):
    bet_amount = int(15)

    if bet_amount:
        bet_amount = int(bet_amount)
        telegram_user = await TelegramUser.objects.filter(telegram_id=callback.from_user.id).afirst()
        if not telegram_user:
            await callback.answer("Пользователь не найден.")
            return

        if bet_amount > 0 and telegram_user.balance >= bet_amount:
            telegram_user.balance -= bet_amount
            await telegram_user.asave()

            category_id = 1  # Замените на вашу логику выбора категории
            item = spin_roulette2(category_id)
            # Определяем результат игры

            win_amount = int(item.name)
            if win_amount > 0:
                telegram_user.balance += win_amount
                result_text = f"Поздравляем! Вы выиграли {win_amount}₽ 🎉"
                outcome = "Победа"
            else:
                result_text = "Увы, вы ничего не выиграли. Попробуйте снова!"
                outcome = "Проигрыш"

            await telegram_user.asave()
            # Сохраняем историю игры
            await save_game_history(telegram_user, "Рулетка 🎡", bet_amount, win_amount, outcome)

            await callback.answer()
            await callback.message.edit_media(
                media=InputMediaPhoto(media="https://placehold.co/500x300/png/?text=Выберете режим",
                                      caption=f"🎰 {result_text}\n"
                f"Ваш баланс: {telegram_user.balance}₽\nЧтобы попробовать снова, введите ставку или используйте /start для выхода."),
                reply_markup=roulette_keyboard())

        else:
            await callback.answer("Недостаточно средств для ставки. Пополните баланс.")
    else:
        await callback.answer("Недопустимая ставка. Пожалуйста, введите сумму ставки в числовом формате.")


# Обработчик нажатия кнопки рулетки
#@router.callback_query(lambda c: c.data == 'spin_roulette')
#async def spin_roulette(callback_query: CallbackQuery):
#    result = random.choice(roulette_results)
#    category_id = 1  # Замените на вашу логику выбора категории
#    item = spin_roulette2(category_id)
#    await callback_query.message.answer(f"Вы выиграли: {item.name}!")
#    await callback_query.answer()


