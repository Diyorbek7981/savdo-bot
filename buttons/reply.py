from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import ADMIN

translations = {
    "uz": "📝 Ro'yhatdan o'tish",
    "ru": "📝 Регистрация"
}


def get_menu(language: str):
    text = translations.get(language, translations["uz"])

    register_menu = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=text)]
        ],
        resize_keyboard=True
    )
    return register_menu


share_contact_text = {
    "uz": "📲 Kontakt ulashish",
    "ru": "📲 Поделиться контактом"
}


def get_phone(language: str):
    text = share_contact_text.get(language, share_contact_text["uz"])

    phone = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=text, request_contact=True)]
        ],
        resize_keyboard=True
    )
    return phone


confirm_text = {
    "uz": "✅ Tasdiqlash",
    "ru": "✅ Подтвердить"
}


def check(language: str):
    text = confirm_text.get(language, confirm_text["uz"])
    check = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=text),
            ],
            [
                KeyboardButton(text='/new'),
            ],
            [
                KeyboardButton(text='/stop'),
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Select the required section'
    )
    return check


def check_after_reg(language: str):
    text = confirm_text.get(language, confirm_text["uz"])
    check_after_reg = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=text),
            ],
            [
                KeyboardButton(text='/new'),
            ],
            [
                KeyboardButton(text='/stop'),
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Select the required section'
    )
    return check_after_reg


messages = {
    "uz": "🛒 Buyurtma berish",
    "ru": "🛒 Сделать заказ"
}

change_language_text = {
    "uz": "🌐 Tilni o‘zgartirish",
    "ru": "🌐 Изменить язык"
}

orders_status_text = {
    "uz": "📦 Buyurtmalarim holati",
    "ru": "📦 Статус моих заказов"
}

rating_text = {
    "uz": "📊 Reyting",
    "ru": "📊 Рейтинг"
}


def menu(language: str):
    # mavjud matnlar
    text = messages.get(language, messages["uz"])
    tet = change_language_text.get(language, change_language_text["uz"])
    txt = orders_status_text.get(language, orders_status_text["uz"])
    tgt = rating_text.get(language, rating_text["uz"])

    # menyu tugmalari
    buttons = [
        [KeyboardButton(text=text)],
        [KeyboardButton(text=tet)],
        [KeyboardButton(text=txt)],
        [KeyboardButton(text="📊 Reyting")]
    ]
    # klaviatura shakllantirish
    phone = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )
    return phone


complate_order = {
    "uz": "✅ Buyurtmani yakunlash",
    "ru": "✅ Завершить заказ"
}


def comp_ord(language: str):
    text = complate_order.get(language, complate_order["uz"])

    ord = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=text)
            ],
        ],
        resize_keyboard=True
    )
    return ord
