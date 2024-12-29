from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from main.management.commands.tgbot.handlers.games.factory import GameCbData, GameActions
from main.management.commands.tgbot.handlers.method import games_list
from main.management.commands.tgbot.keyboards.inline import MenuActions, MenuCbData




def build_products_kb(games):
    builder = InlineKeyboardBuilder()
    for game in games:
        builder.button(
            text=f"{game.name}",  # Display game name and price
            callback_data=GameCbData(
                action=GameActions.details,
                id=1,
                title=game.name,
                code=game.code,
                min_bet=game.min_bet,
            ).pack(),  # Ensure this packs to a valid callback data string
        )


    back = InlineKeyboardButton(text="⬅️ Назад",  callback_data=MenuCbData(action=MenuActions.root).pack())
    builder.add(back)
    builder.adjust(1)
    return builder.as_markup()

