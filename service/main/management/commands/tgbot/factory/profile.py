from enum import IntEnum, auto
from aiogram.filters.callback_data import CallbackData

class ProfileActions(IntEnum):
    edit_profile = auto()
    game_history = auto()
    ranking_achievements = auto()
    referral_system = auto()
    account = auto()
    activate_promo = auto()
    root = auto()

class ProfileCbData(CallbackData, prefix="my_profile"):
    action: ProfileActions
