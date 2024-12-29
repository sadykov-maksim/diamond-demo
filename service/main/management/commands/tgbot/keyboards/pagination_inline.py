from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.db.models import QuerySet

from main.management.commands.tgbot.factory.menu import MenuCbData, MenuActions
from main.management.commands.tgbot.factory.support import PaginationData, PageActions, AnswerCbData, AnswerActions
from main.management.commands.tgbot.handlers.method import get_faq


async def pagination_faq_keyboard(data: QuerySet, page: int = 0, items_per_page: int = 4) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    # Получаем все вопросы
    data_array = list(data)

    # Рассчитываем общее количество страниц
    total_pages = (len(data_array) + items_per_page - 1) // items_per_page

    # Определяем диапазон вопросов для текущей страницы
    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    # Добавление кнопок с вопросами на текущую страницу
    for item in data_array[start_offset:end_offset]:
        builder.button(
            text=str(item),
            callback_data=AnswerCbData(
                action=AnswerActions.details,
                id=item.id,
                callback_data=item.callback_data
            ),
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
    ) if end_offset < len(data_array) else InlineKeyboardButton(
        text="🚫", callback_data=PaginationData(action=PageActions.no_action, page=page).pack()
    )

    # Индикация текущей страницы
    page_indicator = InlineKeyboardButton(
        text=f"📄 {page + 1} из {total_pages}",
        callback_data=PaginationData(action=PageActions.counter, page=page).pack()
    )

    # Кнопка "Вернуться" (ссылка на предыдущую страницу или экран)
    back_button = InlineKeyboardButton(
        text="🔙 Вернуться",
        callback_data=MenuCbData(action=MenuActions.support).pack()
    )


    # Строка с кнопками навигации
    builder.row(prev_button, page_indicator, next_button)
    builder.row(back_button)

    return builder.as_markup()


