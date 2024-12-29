from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from main.management.commands.tgbot.factory.menu import MenuCbData, MenuActions
from main.management.commands.tgbot.factory.profile import ProfileCbData, ProfileActions
from main.management.commands.tgbot.factory.referral import ReferralCbData, ReferralActions


def get_profile_menu():
    buttons = [
        [
            InlineKeyboardButton(text="📝 Изменить профиль", callback_data=ProfileCbData(action=ProfileActions.edit_profile).pack()),

        ],
        [
            InlineKeyboardButton(text="🎮 История игр", callback_data=ProfileCbData(action=ProfileActions.game_history).pack()),
            InlineKeyboardButton(text="🏆 Игровая активность", callback_data=ProfileCbData(action=ProfileActions.ranking_achievements).pack()),

        ],
        [
            InlineKeyboardButton(text="📋 Реферальная система", callback_data=ProfileCbData(action=ProfileActions.referral_system).pack()),
            InlineKeyboardButton(text="🔐 Мой счет", callback_data=ProfileCbData(action=ProfileActions.account).pack()),
        ],
        [
            InlineKeyboardButton(text="🎫 Активировать промокод", callback_data=ProfileCbData(action=ProfileActions.activate_promo).pack()),
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data=MenuCbData(action=MenuActions.root).pack()),
        ],
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )

    return keyboard

def referral_keyboard(share_text):
    buttons = [
        [
            InlineKeyboardButton(text="📢 Поделиться ссылкой", switch_inline_query=share_text),
        ],
        [
            InlineKeyboardButton(text="👥 Мои рефералы", callback_data=ReferralCbData(action=ReferralActions.my_referrals).pack()),
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data=MenuCbData(action=MenuActions.my_profile).pack()),
        ],
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )
    return keyboard


def referrals_keyboard(share_text):
    buttons = [
        [
            InlineKeyboardButton(text="📢 Поделиться ссылкой", switch_inline_query=share_text),
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data=ProfileCbData(action=ProfileActions.referral_system).pack())
        ]
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )
    return keyboard


def my_account_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="💰 Пополнение средств", callback_data="d"),
            InlineKeyboardButton(text="💸 Вывод средств", callback_data="e"),
        ],
        [
            InlineKeyboardButton(text="📊 История транзакций", callback_data="transaction_history"),
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data=MenuCbData(action=MenuActions.my_profile).pack()),
        ]
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )
    return keyboard

def transaction_history_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data=ProfileCbData(action=ProfileActions.root).pack())
        ]
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )
    return keyboard