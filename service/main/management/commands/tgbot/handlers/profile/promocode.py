from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InputMediaPhoto


from main.management.commands.tgbot.factory.profile import ProfileCbData, ProfileActions
from main.management.commands.tgbot.factory.promocode import PromocodeCbData, PromocodeActions
from main.management.commands.tgbot.handlers.method import show_promo
from main.management.commands.tgbot.handlers.profile.profile import router
from main.management.commands.tgbot.misc.states import PromoCodeStates
from main.models import TelegramUser, PromoCode


@router.callback_query(ProfileCbData.filter(F.action == ProfileActions.activate_promo))
async def request_promo_code(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(PromoCodeStates.waiting_for_promo_code)
    await callback_query.message.edit_media(
        media=InputMediaPhoto(
            media="https://placehold.co/500x300/png/?text=Активный промокод",
            caption=(
                f"<b>Введите код и получите бонусы на ваш аккаунт.</b>"
            ),
            parse_mode="HTML"
        ),
    )


@router.message(PromocodeCbData.filter(F.action == PromocodeActions.activate))
@router.message(PromoCodeStates.waiting_for_promo_code)
async def activate_promo_code(message: Message, state: FSMContext):
    promo_code = message.text.strip()
    user_id = message.from_user.id
    try:
        # Retrieve the promo code from the database
        promo = PromoCode.objects.get(code=promo_code, is_active=True)

        # Check if the user has already used this promo code
        if promo.used_by.filter(telegram_id=user_id).exists():
            await message.answer("Вы уже использовали этот промокод.")
            return

        # Apply the promo code effect (e.g., increase user's balance)
        account = TelegramUser.objects.get(telegram_id=user_id)
        account.balance += promo.discount_amount  # Adjust this according to your logic
        account.save()

        # Mark the promo code as used by this user
        promo.used_by.add(account)

        await message.answer(
            f"Промокод {promo_code} успешно активирован! Ваш баланс обновлен на {promo.discount_amount} ₽.")

    except PromoCode.DoesNotExist:
        await show_promo(message)


    except Exception as e:
        await message.answer("Произошла ошибка при активации промокода. Пожалуйста, попробуйте еще раз.")
        print(f"Error in activate_promo_code: {e}")

    finally:
        # Reset the state after processing
        pass
        #await state.clear()
