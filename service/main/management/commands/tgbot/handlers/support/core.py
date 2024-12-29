from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from django.contrib.auth import get_user
from django.template.context_processors import media

from main.management.commands.tgbot.factory.support import SupportCbData, SupportActions, MyRequestsCbData, \
    MyRequestsActions
from main.management.commands.tgbot.keyboards.inline import my_requests_keyboard
from main.management.commands.tgbot.misc.states import WithdrawalState

from deposit_withdrawal.models import WithdrawalRequest

router = Router()

# Обработчик для получения пользовательской суммы пополнения
@router.callback_query(SupportCbData.filter(F.action == SupportActions.support_history))
async def request_custom_deposit_amount(callback_query: CallbackQuery, state: FSMContext):
    """
    Хендлер для отображения заявок пользователя.
    """
    user_id = callback_query.from_user.id
    requests = WithdrawalRequest.objects.filter(user__telegram_id=user_id).order_by('-created_at')

    if not requests.exists():
        await callback_query.message.edit_media(media=InputMediaPhoto(media="https://placehold.co/500x500/png", caption="📝 У вас нет заявок на вывод средств."),
            reply_markup=my_requests_keyboard()
        )
        return

    message_text = "📄 <b>Ваши заявки на вывод:</b>\n\n"
    for req in requests:
        notes = "123"
        print(req.get_status_display())

        if (req.get_status_display() == "Одобрена"):
            print(req.method)
            match req.method:
                case "Криптовалюта":
                    notes = f"<b>Пожалуйста, создайте тикет в поддержку с темой «Вывод средств #REQ_PAYMENT_{req.id}» и укажите в сообщении реквизиты вашего криптокошелька. Заявка будет обработана автоматически без участия оператора.</b>"
                case "карта":
                    notes = f"<b>Пожалуйста, создайте тикет в поддержку с темой «Вывод средств #REQ_PAYMENT_{req.id}» и укажите в сообщении реквизиты вашей банковской карты. Заявка будет обработана автоматически без участия оператора.</b>"
                case _:
                    notes = f"123"

        else:
            notes = req.notes
        message_text += (
            f"🆔 Заявка #{req.id}\n"
            f"💵 Сумма: {req.amount} руб.\n"
            f"📤 Метод: {req.method}\n"
            f"📤 Комментарий: {notes}\n"
            f"📅 Создана: {req.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"🔄 Статус: <b>{req.get_status_display()}</b>\n\n"
        )

    await callback_query.message.edit_media(media=InputMediaPhoto(media="https://placeholder.co/500x500", caption=message_text),
                                            reply_markup=my_requests_keyboard(), parse_mode="HTML")
    await state.set_state(WithdrawalState.enter_amount)


@router.callback_query(lambda c: c.data == "my_requests")
async def show_my_requests(callback_query: CallbackQuery):
    """
    Хендлер для отображения заявок пользователя.
    """
    user_id = callback_query.from_user.id
    requests = WithdrawalRequest.objects.filter(user__telegram_id=user_id).order_by('-created_at')

    if not requests.exists():
        await callback_query.message.edit_text(
            "📝 У вас нет заявок на вывод средств.",
            reply_markup=my_requests_keyboard()
        )
        return

    message_text = "📄 <b>Ваши заявки на вывод:</b>\n\n"
    for req in requests:
        message_text += (
            f"🆔 Заявка #{req.id}\n"
            f"💵 Сумма: {req.amount} руб.\n"
            f"📤 Метод: {req.method}\n"
            f"📅 Создана: {req.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"🔄 Статус: <b>{req.get_status_display()}</b>\n\n"
        )

    await callback_query.message.edit_media(media=InputMediaPhoto(media="https://placeholder.co/500x500", caption=message_text),
                                            reply_markup=my_requests_keyboard(), parse_mode="HTML")


@router.callback_query(MyRequestsCbData.filter(F.action == MyRequestsActions.refresh))
async def refresh_my_requests(callback_query: CallbackQuery):
    """
    Хендлер для обновления списка заявок.
    """
    await show_my_requests(callback_query)