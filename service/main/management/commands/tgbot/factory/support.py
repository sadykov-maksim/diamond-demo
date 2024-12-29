from enum import IntEnum, auto
from aiogram.filters.callback_data import CallbackData


class SupportActions(IntEnum):
    start_chat = auto()
    support_history = auto()
    faq = auto()
    report_issue = auto()

class SupportCbData(CallbackData, prefix="support"):
    action: SupportActions


class FaqActions(IntEnum):
    start_chat = auto()
    edit_answer = auto()
    understood = auto()
    not_clear = auto()
    root = auto()

class FaqCbData(CallbackData, prefix="faq"):
    action: FaqActions


class AnswerActions(IntEnum):
    details = auto()
    edit_answer = auto()
    understood = auto()
    not_clear = auto()

class AnswerCbData(CallbackData, prefix="faq"):
    action: AnswerActions
    id: int
    callback_data: str


class MyRequestsActions(IntEnum):
    refresh = auto()

class MyRequestsCbData(CallbackData, prefix="my_requests"):
    action: MyRequestsActions


class PageActions(IntEnum):
    no_action = auto()
    page_info = auto()
    counter = auto()

class PaginationData(CallbackData, prefix="paginate"):
    action: PageActions
    page: int
