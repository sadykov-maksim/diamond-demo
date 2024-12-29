from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from main.management.commands.tgbot.factory.menu import MenuCbData, MenuActions
from main.management.commands.tgbot.factory.profile import ProfileCbData, ProfileActions
from main.management.commands.tgbot.factory.promocode import PromocodeCbData, PromocodeActions
from main.management.commands.tgbot.factory.support import SupportCbData, SupportActions, MyRequestsCbData, \
    MyRequestsActions



# This is a simple keyboard, that contains 2 buttons
def continue_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="✅ Продолжить",
                                 callback_data="continue_action"),
        ],
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )
    return keyboard

def age_verification_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="✅ Да, мне 18+", callback_data="age_yes"),
            InlineKeyboardButton(text=" ❌ Нет, мне меньше 18", callback_data="age_no"),
        ],
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )
    return keyboard


def accept_agreement_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="✅ Я согласен с условиями",
                                 callback_data="accept_agreement"),
            InlineKeyboardButton(text="❌ Отказаться",
                                 callback_data="waiver_agreement"),
        ],
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )
    return keyboard



def beginning_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="📋 Перейти в меню", callback_data="main_menu"),
        ],
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )
    return keyboard


def navigation_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="🎮 Мини-игры", callback_data=MenuCbData(action=MenuActions.mini_games).pack()),
            InlineKeyboardButton(text="👤 Мой профиль", callback_data=MenuCbData(action=MenuActions.my_profile).pack()),
        ],
        [
            InlineKeyboardButton(text="💰 Пополнение и вывод", callback_data=MenuCbData(action=MenuActions.deposit_withdrawal).pack()),
        ],
        [
            InlineKeyboardButton(text="⚙️ Настройки", callback_data=MenuCbData(action=MenuActions.settings).pack()),
            InlineKeyboardButton(text="💬 Помощь", callback_data=MenuCbData(action=MenuActions.support).pack()),
        ],
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )
    return keyboard


def roulette_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="Крутить рулетку 🎲", callback_data="spin_roulette"),
        ],
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )
    return keyboard

def barrels_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="Поставить ставку 🎲", callback_data="place_bet"),
        ],
        [
            InlineKeyboardButton(text="📋 Перейти в меню", callback_data="main_menu"),
        ]
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )
    return keyboard



def promo_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="🔄 Пробовать снова",
                                 callback_data=ProfileCbData(action=ProfileActions.activate_promo).pack()),
            InlineKeyboardButton(text="⬅️ Вернуться",
                                 callback_data=MenuCbData(action=MenuActions.my_profile).pack()),
        ],
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )
    return keyboard

def game_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="🎰 Крутить админа",
                                 web_app=WebAppInfo(url=f'https://red-caviar-wholesale.host//')),
        ],
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )
    return keyboard

def my_requests_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔍 Обновить заявки", callback_data=MyRequestsCbData(action=MyRequestsActions.refresh).pack())],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data=MenuCbData(action=MenuActions.support).pack())],
        ]
    )



def support_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="💬 Начать чат с поддержкой", switch_inline_query="share_text", url="https://t.me/YourSupportUsername"),
            InlineKeyboardButton(text="📂 История заявок", callback_data=SupportCbData(action=SupportActions.support_history).pack()),
        ],
        [
            InlineKeyboardButton(text="❓ Вопросы и ответы", callback_data=SupportCbData(action=SupportActions.faq).pack()),
            InlineKeyboardButton(text="🚨 Сообщить о проблеме", callback_data=SupportCbData(action=SupportActions.report_issue).pack()),
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data=MenuCbData(action=MenuActions.root).pack()),
        ],
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )
    return keyboard