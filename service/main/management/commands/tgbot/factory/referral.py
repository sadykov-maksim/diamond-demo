from enum import IntEnum, auto
from aiogram.filters.callback_data import CallbackData

class ReferralActions(IntEnum):
    my_referrals = auto()


class ReferralCbData(CallbackData, prefix="referral"):
    action: ReferralActions
