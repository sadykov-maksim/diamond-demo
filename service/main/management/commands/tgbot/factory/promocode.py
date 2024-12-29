from enum import IntEnum, auto
from aiogram.filters.callback_data import CallbackData

class PromocodeActions(IntEnum):
    activate = auto()
    root = auto()

class PromocodeCbData(CallbackData, prefix="promocode"):
    action: PromocodeActions
