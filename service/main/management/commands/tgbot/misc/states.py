from aiogram.fsm.state import StatesGroup, State


class WithdrawalState(StatesGroup):
    initial_state = State()
    enter_amount = State()
    select_method = State()
    confirm = State()  # Подтверждение вывода

class PromoCodeStates(StatesGroup):
    waiting_for_promo_code = State()

class UserStates(StatesGroup):
    waiting_for_action = State()
    waiting_for_deposit_amount = State()
    waiting_for_withdrawal_amount = State()
    waiting_for_custom_deposit_amount = State()
    replenishment_balance = State()
    check_balance = State()

class RegistrationSteps(StatesGroup):
    check_referral = State()
    check_subscription = State()

class Main_menu(StatesGroup):
    main_menu = State()

class ProfileEdit(StatesGroup):
    waiting_for_name = State()
    waiting_for_email = State()
    waiting_for_notifications = State()

class ReportProblem(StatesGroup):
    waiting_for_problem = State()
    sending_request = State()


class Form(StatesGroup):
    state_1 = State()  # Состояние для ввода ставки
    state_2 = State()  # Состояние для ввода ставки
    state_3 = State()  # Состояние для ввода ставки

class Roulette(StatesGroup):
    state_1 = State()  # Состояние для ввода ставки
    state_2 = State()  # Состояние для ввода ставки
    state_3 = State()  # Состояние для ввода ставки


class Chests(StatesGroup):
    state_1 = State()  # Состояние для ввода ставки
    state_2 = State()  # Состояние для ввода ставки
    state_3 = State()  # Состояние для ввода ставки

