from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, InputMediaPhoto


from main.management.commands.tgbot.factory.profile import ProfileCbData, ProfileActions
from main.management.commands.tgbot.factory.referral import ReferralCbData, ReferralActions
from main.management.commands.tgbot.handlers.profile.profile import router
from main.management.commands.tgbot.keyboards.profile_inline import referral_keyboard, referrals_keyboard
from main.models import TelegramUser

@router.callback_query(ProfileCbData.filter(F.action == ProfileActions.referral_system))
async def referral_system(callback_query: CallbackQuery):
    try:
        # Получение имени бота
        bot_info = await callback_query.bot.get_me()
        bot_username = bot_info.username

        # Count the number of referrals
        referrer_count = TelegramUser.objects.filter(referer=callback_query.from_user.id).count()
        #await callback_query.message.delete()

        # Формирование ссылки с динамическим именем бота
        referral_link = f"https://t.me/{bot_username}?start={callback_query.from_user.id}"
        share_text = f"Привет! 🎉 Я зарегистрировался в боте и получил бонус! Присоединяйся тоже: {referral_link}"

        # Edit the message to show referral information
        await callback_query.message.edit_media(
            media=InputMediaPhoto(
                media="https://placehold.co/500x300/png/?text=Реферальная+система",
                caption=(
                    f"<b>Приглашайте друзей и получайте бонусы за каждого нового игрока! 💸</b>\n\n"
                    f"🌟 Поделитесь этой ссылкой с друзьями: \n"
                    f"👉 {referral_link}\n\n"
                    f"<b>Ваши бонусы за каждого приглашенного игрока:</b>\n"
                    f"💰 <b>15% от пополнения счета рефералом.</b>\n"
                    f"🔄 <b>1% от каждой игровой сессии приглашенного друга.</b>\n\n"
                    f"<b>Что получает ваш друг: </b>\n"
                    f"🎁 <b>Бонусный баланс 50 рублей для </b>начала игры.\n"
                    f"💸 <b>Дополнительные 10% к первому пополнению счета.</b>\n\n"
                    f"<b>Ваш текущий реферальный баланс:</b> 0₽\n"
                    f"👥 <b>Количество приглашенных друзей:</b> {referrer_count}"
                ),
                parse_mode="HTML"
            ),
            reply_markup=referral_keyboard(share_text)
        ) 



    except Exception as e:
        # Handle any exceptions that occur
        await callback_query.answer("Произошла ошибка при изменении сообщения. Пожалуйста, попробуйте еще раз.")
        print(f"Error in referral_system: {e}")



@router.callback_query(ReferralCbData.filter(F.action == ReferralActions.my_referrals))
async def show_referrals(callback_query: CallbackQuery):
    try:
        bot_info = await callback_query.bot.get_me()
        bot_username = bot_info.username
        referrals = TelegramUser.objects.filter(referer=callback_query.from_user.id)

        referral_link = f"https://t.me/{bot_username}?start={callback_query.from_user.id}"
        share_text = f"Привет! 🎉 Я зарегистрировался в боте и получил бонус! Присоединяйся тоже: {referral_link}"

        if not referrals:
            message_text = "🔗 *У вас пока нет рефералов.*\n\nПриглашайте друзей и получайте бонусы!"
        else:
            message_text = "🎉 *Ваши рефералы:*\n\n"
            for i, referral in enumerate(referrals, start=1):
                message_text += (
                    f"{i}. 👤 *@{referral.username}*\n"
                    f"   └ ID: `{referral.telegram_id}`\n"
                    f"   └ 📅 Дата регистрации: {referral.date_joined}\n\n"
                )
        await callback_query.message.edit_media(media=InputMediaPhoto(media="https://placehold.co/500x300/png/?text=Мои+рефералы", caption=message_text, parse_mode="Markdown"), reply_markup=referrals_keyboard(share_text))

    except Exception as e:
        await callback_query.answer("Произошла ошибка при изменении сообщения. Пожалуйста, попробуйте еще раз.")
        print(f"Error in referral_system: {e}")
