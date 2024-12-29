from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from django.core.exceptions import ObjectDoesNotExist

from main.management.commands.tgbot.factory.menu import MenuCbData, MenuActions
from main.management.commands.tgbot.handlers.method import get_avatar
from main.management.commands.tgbot.keyboards.profile_inline import get_profile_menu
from main.models import TelegramUser

router = Router()

@router.callback_query(MenuCbData.filter(F.action == MenuActions.my_profile))
async def handle_my_profile_button(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id

    try:
        account = TelegramUser.objects.get(telegram_id=user_id)
    except ObjectDoesNotExist:
        await callback_query.answer("Пользователь не найден.", show_alert=True)
        return

    avatar_file_id = await get_avatar(callback_query.bot, user_id)
    nickname = account.username

    # Вычисляем количество дней с момента регистрации
    days_registered = (datetime.now().date() - account.date_joined).days

    profile_caption = (
        "🧑‍💻 <b>Ваш профиль:</b>\n\n"
        f"🏷️ <b>Никнейм:</b> [<u>{nickname}</u>]\n\n"
        f"🔗 <b>Имя пользователя:</b> @{account.username}\n\n"
        f"📆 <b>Дата регистрации:</b> {account.date_joined.strftime('%d.%m.%Y')} "
        f"(<i>{days_registered} дней с нами</i>)\n"
    )

    await callback_query.message.edit_media(
        media=InputMediaPhoto(media=avatar_file_id, caption=profile_caption, parse_mode="HTML"),
        reply_markup=get_profile_menu()
    )