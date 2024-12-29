

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from main.management.commands.tgbot.factory.menu import MenuCbData, MenuActions
from main.management.commands.tgbot.factory.profile import ProfileCbData, ProfileActions
from main.management.commands.tgbot.factory.referral import ReferralCbData, ReferralActions
from main.management.commands.tgbot.factory.support import FaqCbData, FaqActions, SupportCbData, SupportActions, \
    AnswerCbData, AnswerActions, PaginationData, PageActions
from main.management.commands.tgbot.handlers.method import get_faq
from support.models import FAQ, SupportTicket, TicketType


async def  faq_paginated_keyboard(CallbackData: CallbackData, page: int = 0, items_per_page: int = 4) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    # Получаем все вопросы
    faqs = await get_faq()
    faqs_list = list(faqs)  # Преобразуем QuerySet в список для удобства работы

    # Рассчитываем общее количество страниц
    total_pages = (len(faqs_list) + items_per_page - 1) // items_per_page

    # Определяем диапазон вопросов для текущей страницы
    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    # Добавление кнопок с вопросами на текущую страницу
    for faq in faqs_list[start_offset:end_offset]:
        builder.button(
            text=faq.question,
            callback_data=CallbackData(
                action=CallbackData.details,
                id=faq.id,
                callback_data=faq.callback_data,
            ).pack(),
        )
    builder.adjust(1)

    # Кнопки навигации
    prev_button = InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data=PaginationData(page=page - 1, action=PageActions.page_info).pack()
    ) if page > 0 else InlineKeyboardButton(
        text="🚫", callback_data=PaginationData(action=PageActions.no_action, page=page).pack()
    )

    next_button = InlineKeyboardButton(
        text="➡️ Вперёд",
        callback_data=PaginationData(page=page + 1, action=PageActions.page_info).pack()
    ) if end_offset < len(faqs_list) else InlineKeyboardButton(
        text="🚫", callback_data=PaginationData(action=PageActions.no_action, page=page).pack()
    )

    # Индикация текущей страницы
    page_indicator = InlineKeyboardButton(
        text=f"📄 {page + 1} из {total_pages}",
        callback_data=PaginationData(action=PageActions.counter, page=page).pack()
    )

    # Строка с кнопками навигации
    builder.row(prev_button, page_indicator, next_button)

    return builder.as_markup()




def faq_answer_keyboard(answer_cb_data: AnswerCbData):
    buttons = [
        [
            InlineKeyboardButton(text="👌 Всё понятно", callback_data=AnswerCbData(action=AnswerActions.understood, **answer_cb_data.model_dump(include={"id", "callback_data"})).pack()),
            InlineKeyboardButton(text="🤔 Не совсем понятно", callback_data=AnswerCbData(action=AnswerActions.not_clear, **answer_cb_data.model_dump(include={"id", "callback_data"})).pack()),
        ],

        [
            InlineKeyboardButton(text="⬅️ Назад",  callback_data=SupportCbData(action=SupportActions.faq).pack()),
        ],
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )
    return keyboard

def faq_back_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="⬅️ Назад",  callback_data=SupportCbData(action=SupportActions.faq).pack()),
        ],
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )
    return keyboard

def report_issue_keyboard():
    builder = InlineKeyboardBuilder()

    # Получаем все вопросы
    themes = TicketType.objects.all()


    # Добавление кнопок с вопросами на текущую страницу
    for theme in themes:
        builder.button(
            text=theme.name,
            callback_data=theme.callback
        )
    builder.adjust(1)


    return builder.as_markup()


def edit_faq_answer_keyboard(answer_cb_data: AnswerCbData):
    """
    Создает клавиатуру для редактирования ответа на FAQ.

    :param faq_id: Идентификатор вопроса FAQ, для которого будет происходить редактирование ответа.
    :return: Клавиатура для редактирования ответа на FAQ.
    """
    buttons = [
        [
            InlineKeyboardButton(text="✍️ Изменить ответ",   callback_data=AnswerCbData(action=AnswerActions.edit_answer,  **answer_cb_data.model_dump(include={"id", "callback_data"})).pack()),
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data=SupportCbData(action=SupportActions.faq).pack()),
        ],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard