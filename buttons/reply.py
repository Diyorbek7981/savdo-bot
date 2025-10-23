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
    text = share_contact_text.get(language, translations["uz"])

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
    "uz": "📝 Ruhsatnoma olish",
    "ru": "📝 Получить разрешение"
}

change_language_text = {
    "uz": "🌐 Tilni o‘zgartirish",
    "ru": "🌐 Изменить язык"
}


def menu(language: str):
    text = messages.get(language, translations["uz"])
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
