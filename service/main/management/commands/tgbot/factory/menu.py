from enum import IntEnum, auto

from aiogram.filters.callback_data import CallbackData


class MenuActions(IntEnum):
    mini_games = auto()
    my_profile = auto()
    deposit_withdrawal = auto()
    settings = auto()
    support = auto()
    invite_code = auto()
    visit_website = auto()

    root = auto() #Назад

class MenuCbData(CallbackData, prefix="main_menu"):
    action: MenuActions