from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InputMediaPhoto

from main.management.commands.tgbot.factory.profile import ProfileCbData, ProfileActions
from main.management.commands.tgbot.handlers.method import get_user_balance
from main.management.commands.tgbot.handlers.profile.profile import router
from main.management.commands.tgbot.keyboards.profile_inline import my_account_keyboard, transaction_history_keyboard
from main.models import TransactionHistory


@router.callback_query(ProfileCbData.filter(F.action == ProfileActions.account))
async def my_account_handler(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id

    try:
        account_balance = await get_user_balance(user_id)  # Убедитесь, что функция возвращает корректное число
        currency = "USD"
        withdrawal_limit = 500  # Пример лимита на вывод средств
        last_transaction = "+250"
        transaction_type = "пополнение"

        # Форматирование для более аккуратного отображения
        account_caption = (
            "<b>💼 Ваш счёт:</b>\n\n"
            f"💰 <b>Баланс:</b> <code>{account_balance:.2f} {currency}</code>\n"
            f"🔓 <b>Доступно для вывода:</b> <code>{withdrawal_limit:.2f} {currency}/день</code>\n"
            f"📋 <b>Последняя транзакция:</b> <code>{last_transaction} {currency}</code> ({transaction_type})\n\n"
        )

        # Обновление сообщения с изображением и клавиатурой
        await callback_query.message.edit_media(
            media=InputMediaPhoto(
                media="https://placehold.co/500x300/png/?text=Мой+счет",
                caption=account_caption,
                parse_mode="HTML"
            ),
            reply_markup=my_account_keyboard()  # Убедитесь, что функция возвращает корректную клавиатуру
        )

    except TelegramAPIError as e:
        await callback_query.answer("Произошла ошибка при загрузке информации о счёте.", show_alert=True)
        print(f"Ошибка Telegram API: {e}")
    except Exception as e:
        await callback_query.answer("Не удалось получить данные о счёте.", show_alert=True)
        print(f"Неизвестная ошибка: {e}")

@router.callback_query(lambda c: c.data == 'transaction_history')
async def transaction_history(callback_query: CallbackQuery):
    try:
        # Retrieve the transaction history for the user
        transactions = TransactionHistory.objects.filter(user__telegram_id=callback_query.from_user.id).order_by('-created_at')
        print(transactions)

        if not transactions.exists():
            await callback_query.message.delete()
            await callback_query.message.answer("📜 История транзакций пуста.")
            return

        # Build a message with the transaction details
        transaction_messages = []
        for transaction in transactions:
            transaction_messages.append(
                f"🗓 {transaction.created_at.strftime('%Y-%m-%d %H:%M')}\n"
                f"💵 Сумма: {transaction.amount} ₽\n"
                f"📋 Тип: {'Кредит' if transaction.amount > 0 else 'Дебет'}\n"
                f"✏️ Описание: {transaction.transaction_type}\n"
                "------------------------------------"
            )

        # Join the transaction messages
        transaction_text = "\n\n".join(transaction_messages)

        # Send the transaction history to the user
        await callback_query.message.answer(
            f"📜 Ваша история транзакций:\n\n{transaction_text}",
            reply_markup=transaction_history_keyboard()
        )

    except Exception as e:
        await callback_query.answer("Произошла ошибка при загрузке истории транзакций. Пожалуйста, попробуйте еще раз.")
        print(f"Error in transaction_history: {e}")
