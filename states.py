from aiogram.fsm.state import StatesGroup, State


class SignupStates(StatesGroup):
    name = State()
    age = State()
    phone = State()
    check = State()


class OrderStates(StatesGroup):
    quantity = State()


class CompleteOrderStates(StatesGroup):
    address = State()
    confirm_order = State()
