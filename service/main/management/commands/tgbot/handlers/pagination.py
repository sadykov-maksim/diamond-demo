from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from main.management.commands.tgbot.factory.support import PaginationData, PageActions, AnswerCbData, AnswerActions
from main.management.commands.tgbot.handlers.profile import router
from main.management.commands.tgbot.keyboards.pagination_inline import pagination_faq_keyboard


@router.callback_query(PaginationData.filter(F.action == PageActions.no_action))
async def handle_no_action(callback: CallbackQuery):
    await callback.answer("Навигация в этом направлении недоступна.", show_alert=True)

@router.callback_query(PaginationData.filter(F.action == PageActions.counter))
async def handle_no_action(callback: CallbackQuery, state: FSMContext):
    await state.update_data(chosen_food=callback.data)
    await callback.answer()

@router.callback_query(PaginationData.filter())
async def handle_faq_pagination(call: CallbackQuery, callback_data: PaginationData, state: FSMContext):
    page = callback_data.page
    data = await state.get_data()

    keyboard = await pagination_faq_keyboard(data, page)

    await call.message.edit_reply_markup(reply_markup=keyboard)
    await call.answer()