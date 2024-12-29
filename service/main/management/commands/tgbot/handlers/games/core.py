import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InputMediaPhoto, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils import markdown
from aiogram.utils.keyboard import InlineKeyboardBuilder

from diamond.settings import MEDIA_URL
from main.management.commands.tgbot.handlers.games.factory import GameActions, GameCbData, GameModeCbData, \
    GameModeActions

from main.management.commands.tgbot.handlers.method import games_list

from main.management.commands.tgbot.keyboards.inline import MenuCbData, MenuActions, roulette_keyboard, \
    barrels_keyboard
from main.management.commands.tgbot.misc.states import Form, Roulette, Chests
from main.models import TelegramUser, Game

router = Router()


@router.callback_query(GameCbData.filter(F.action == GameActions.details))
async def show_options(call: CallbackQuery, callback_data: GameCbData, state: FSMContext):
    # Получение пользователя из БД
    telegram_user = await (
        TelegramUser.objects.filter(telegram_id=call.from_user.id).afirst())
    if not telegram_user:
        await call.message.answer("Пользователь не найден.")
        return

    # Проверка, есть ли у пользователя минимальный баланс для ставки
    min_bet = 100  # Минимальная сумма ставки для игры
    if telegram_user.balance < min_bet:
        await call.message.answer(f"Ваш баланс: {telegram_user.balance}\n"
                                            "У вас недостаточно средств для игры. Пожалуйста, пополните баланс.")
        return


    match callback_data.code:
        case "faad84f0":
            await call.message.edit_media(
                media=InputMediaPhoto(media="https://placehold.co/500x300/png/?text=Выберете режим",
                                      caption=f"Добро пожаловать в игру {callback_data.title}! 🎉\n"
                                              "Пожалуйста, сделайте ставку, чтобы испытать удачу!\n"
                                              "Введите сумму ставки (например: 100):"),
                reply_markup=product_details_kb(callback_data))
            await state.set_state(Form.state_1)
        case "0337b770":
            await call.message.edit_media(
                media=InputMediaPhoto(media="https://placehold.co/500x300/png/?text=Выберете режим",
                                      caption=f"Добро пожаловать в игру '{callback_data.title}'!"
                                              f" Нажмите на кнопку, чтобы испытать удачу."),
                reply_markup=product_details_kb(callback_data))
        case "chests":
            await call.message.edit_media(
                media=InputMediaPhoto(media="https://placehold.co/500x300/png/?text=Выберете режим",
                                      caption=f"Добро пожаловать в игру '{callback_data.title}'!"
                                              f" Нажмите на кнопку, чтобы испытать удачу."),
                reply_markup=product_details_kb(callback_data))
            await state.set_state(Chests.state_1)

        case _:
            await call.message.edit_media(
                media=InputMediaPhoto(media="https://placeholder.co/500x500",
                                      caption="Игра не выбрана"))



@router.callback_query(GameCbData.filter(F.action == GameActions.text))
async def handle_product_details_button(call: CallbackQuery, callback_data: GameCbData, state: FSMContext):
    await call.answer()

    telegram_user = await (
        TelegramUser.objects.filter(telegram_id=call.from_user.id).afirst())
    if not telegram_user:
        await call.message.answer("Пользователь не найден.")
        return

    min_bet = callback_data.min_bet
    if telegram_user.balance < min_bet:
        await call.message.answer(f"Ваш баланс: {telegram_user.balance}\n"
                                            "У вас недостаточно средств для игры. Пожалуйста, пополните баланс.", show_alert=True)
        return


    match callback_data.code:
        case "faad84f0":
            await call.message.edit_media(
                media=InputMediaPhoto(media="https://placehold.co/500x300/png/?text=Выберете режим",
                                      caption=f"Добро пожаловать в игру {callback_data.title}! 🎉\n"
                                              "Пожалуйста, сделайте ставку, чтобы испытать удачу!\n"
                                              "Введите сумму ставки (например: 100):"),
                )
            await state.set_state(Form.state_1)
        case "0337b770":
            await call.message.edit_media(
                media=InputMediaPhoto(media="https://placehold.co/500x300/png/?text=Выберете режим",
                                      caption=f"Добро пожаловать в игру {callback_data.title}! 🎉\n"
                                              "Пожалуйста, сделайте ставку, чтобы испытать удачу!\n"
                                              "Введите сумму ставки (например: 100):"),
                reply_markup=roulette_keyboard())
            await state.set_state(Roulette.state_1)

        case "chests":
            game = Game.objects.filter(is_active=True).first()

            if not game or not game.banner:
                await call.message.answer("Не удалось загрузить баннер для игры. Попробуйте позже.")
                return

            banner_url = game.banner.url

            try:
                print(f"Banner URL: {banner_url}")
                await call.message.edit_media(
                    media=InputMediaPhoto(
                        media=banner_url,
                        caption=(
                            f"Добро пожаловать в игру {callback_data.title}! 🎉\n"
                            "Пожалуйста, сделайте ставку, чтобы испытать удачу!\n"
                            "Введите сумму ставки (например: 100):"
                        ),
                    ),
                )
                await state.set_state(game.state)
            except Exception as e:
                print(f"Error updating media: {e}")
                await call.message.answer("Произошла ошибка при загрузке баннера.")

        case _:
            await call.message.edit_media(
                media=InputMediaPhoto(media="https://placeholder.co/500x500",
                                      caption="Игра не выбрана"))






def build_update_product_kb(
    product_cb_data: GameCbData,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=f"⬅️ back to {product_cb_data.title}",
        callback_data=GameCbData(
            action=GameActions.text,
            **product_cb_data.model_dump(include={"id", "title", "link"}),
        ),
    )
    builder.button(
        text="🔄 Update",
        callback_data="...",
    )
    return builder.as_markup()

def product_details_kb(
    product_cb_data: GameCbData,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for label, action in [
        ("🎮 Начать игру", GameActions.text),
    ]:
        builder.button(
            text=label,
            callback_data=GameCbData(
                action=action,
                **product_cb_data.model_dump(include={"id", "title", "code", "min_bet"}),
            ),
        )

    back = InlineKeyboardButton(text="⬅️ Выбрать другой режим",  callback_data=MenuCbData(action=MenuActions.mini_games).pack())
    builder.add(back)
    builder.adjust(1,1)
    return builder.as_markup()