from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton

from main.management.commands.tgbot.factory.support import SupportCbData, SupportActions, FaqCbData, FaqActions, \
    AnswerCbData, AnswerActions
from main.management.commands.tgbot.handlers.method import create_support_ticket, get_faq, get_answer_for_faq
from main.management.commands.tgbot.handlers.profile import router
from main.management.commands.tgbot.keyboards.pagination_inline import pagination_faq_keyboard
from main.management.commands.tgbot.keyboards.support_inline import faq_answer_keyboard, \
    edit_faq_answer_keyboard, faq_back_keyboard, report_issue_keyboard
from main.management.commands.tgbot.misc.states import ReportProblem
from support.models import FAQ, FAQFeedback



@router.callback_query(SupportCbData.filter(F.action == SupportActions.faq))
async def faq_command(callback: CallbackQuery):
    faq = await get_faq()
    await callback.message.edit_media(
        media=InputMediaPhoto(media="https://placehold.co/500x300/png/?text=FAQ", caption="Выберите вопрос, чтобы получить ответ:"),
        reply_markup=await pagination_faq_keyboard(faq)
    )



# Обработчик нажатия на кнопку FAQ
@router.callback_query(AnswerCbData.filter(F.action == AnswerActions.details))
async def faq_answer_callback(    call: CallbackQuery,
    callback_data: AnswerCbData):
    question_key = callback_data.callback_data
    answer = await get_answer_for_faq(callback_data.callback_data)  # Получаем ответ на вопрос

    # Получаем пользователя
    user = call.from_user.id

    # Проверяем, оставил ли пользователь отзыв для этого вопроса
    feedback_exists = FAQFeedback.feedback_exists(user, question_key)

    # Формируем клавиатуру в зависимости от того, оставлен ли отзыв
    if feedback_exists:
        # Клавиатура для пользователей с оценкой
        keyboard = edit_faq_answer_keyboard(callback_data)
    else:
        # Клавиатура для пользователей без оценки
        keyboard = faq_answer_keyboard(callback_data)

    # Отправляем сообщение с медиа и клавиатурой
    await call.message.edit_media(
        media=InputMediaPhoto(media="https://placehold.co/500x300/png/?text=FAQ", caption=f"<b>{answer.question}</b>\n\n{answer.answer}"),
        reply_markup=keyboard
    )

    # Подтверждаем обработку callback
    await call.answer()


@router.callback_query(AnswerCbData.filter(F.action == AnswerActions.edit_answer))
async def handle_edit_faq_answer(callback_query: CallbackQuery, state: FSMContext, callback_data: AnswerCbData):
    try:
        #faq_q = FAQ.get_questions_by_filter(faq)
        faqs = FAQ.get_question(callback_data.callback_data)

        # Отправляем сообщение с просьбой ввести новый ответ
        await callback_query.message.edit_media(media=InputMediaPhoto(media="https://placehold.co/500x500/png", caption=f"<b>{faqs.question}</b>\n\n{faqs.answer}\n\nПожалуйста, выберите новый ответ для этого вопроса:", parse_mode="HTML"), reply_markup=faq_answer_keyboard(callback_data))
        await callback_query.answer()

    except FAQ.DoesNotExist:
        await callback_query.answer("Этот вопрос не найден.")

@router.callback_query(SupportCbData.filter(F.action == SupportActions.report_issue))
async def report_problem_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_media(
        media=InputMediaPhoto(media="https://placehold.co/500x300/png/?text=FAQ", caption=f"📝 Выберите подходящую тему для вашего обращения, чтобы мы могли быстрее вам помочь."), reply_markup=report_issue_keyboard())
    await state.set_state(ReportProblem.waiting_for_problem)


@router.callback_query(AnswerCbData.filter(F.action == AnswerActions.understood))
async def faq_command(callback: CallbackQuery, state: FSMContext, callback_data: AnswerCbData):
    answer = await get_answer_for_faq(callback_data.callback_data)
    answer.add_feedback(answer.callback_data, callback.from_user.id, True)
    await callback.message.edit_media(
        media=InputMediaPhoto(media="https://placehold.co/500x300/png/?text=RES", caption="Спасибо за оценку",
                              parse_mode="HTML"), reply_markup=faq_back_keyboard())

@router.callback_query(AnswerCbData.filter(F.action == AnswerActions.not_clear))
async def faq_command(callback: CallbackQuery, state: FSMContext, callback_data: AnswerCbData):
    answer = await get_answer_for_faq(callback_data.callback_data)
    answer.add_feedback(answer.callback_data, callback.from_user.id, False)
    await callback.message.edit_media(
        media=InputMediaPhoto(media="https://placehold.co/500x300/png/?text=RES", caption="Спасибо за оценку",
                              parse_mode="HTML"), reply_markup=faq_back_keyboard())



# Обработка введенного описания проблемы
@router.callback_query(ReportProblem.waiting_for_problem)
async def process_problem(callback: CallbackQuery, state: FSMContext):
    await state.update_data(subject=callback.data)

    await callback.message.edit_media(
        media=InputMediaPhoto(media="https://placehold.co/500x300/png/?text=FAQ", caption=f"📝 Пожалуйста, опишите проблему в деталях и уточните, в каком разделе вы столкнулись с ошибкой.") )
    await state.set_state(ReportProblem.sending_request)



# Обработка введенного описания проблемы
@router.message(ReportProblem.sending_request)
async def process_problem(message: Message, state: FSMContext):
    problem_text = message.text  # Получаем текст проблемы
    user_data = await state.get_data()
    print(user_data)
    # ID администратора или группы поддержки (замените на реальный)
    admin_id = 5313523026

    try:
        ticket = await create_support_ticket(user_data['subject'], message.from_user.id, problem_text)
        await message.answer(ticket)
    except ValueError as ex:
        print(ex)
    # Отправка сообщения админу
    await message.bot.send_message(
        admin_id,
        f"⚠️ Новое сообщение о проблеме от пользователя {message.from_user.full_name} (@{message.from_user.username}):\n\n{problem_text}"
    )
    await state.clear()  # Завершаем состояние

