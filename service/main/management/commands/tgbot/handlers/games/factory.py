from enum import IntEnum, auto

from aiogram.filters.callback_data import CallbackData


class GameModeActions(IntEnum):
    left = auto()
    right = auto()

class GameModeCbData(CallbackData, prefix="game_mode"):
    action: GameModeActions



class GameActions(IntEnum):
    details = auto()
    text = auto()
    graphics = auto()

class GameCbData(CallbackData, prefix="game"):
    action: GameActions
    id: int
    title: str
    code: str
    min_bet: int


