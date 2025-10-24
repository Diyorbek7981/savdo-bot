from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

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


check = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='✔️'),
        ],
        [
            KeyboardButton(text='/new'),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Select the required section'
)

messages = {
    "uz": "🛒 Buyurtma berish",
    "ru": "🛒 Сделать заказ"
}

change_language_text = {
    "uz": "🌐 Tilni o‘zgartirish",
    "ru": "🌐 Изменить язык"
}


def menu(language: str):
    text = messages.get(language, messages["uz"])
    tet = change_language_text.get(language, change_language_text["uz"])

    phone = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=text)
            ],
            [
                KeyboardButton(text=tet)
            ]
        ],
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
