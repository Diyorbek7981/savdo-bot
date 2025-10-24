from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

language_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O‘zbek tili", callback_data="stlang_uz"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="stlang_ru"),
        ],
    ], resize_keyboard=True
)


def cat_inline(data: list):
    markup = InlineKeyboardBuilder()
    for item in data:
        markup.button(text=f"{item['name']}",
                      callback_data=f"cat_{item['id']}")
    markup.adjust(1, repeat=True)
    return markup.as_markup()


def prod_inline(data: list):
    markup = InlineKeyboardBuilder()
    for p in data:
        markup.button(text=f"{p['name']} — {p['price']} so‘m/{p['unit']}",
                      callback_data=f"prod_{p['id']}")
    markup.adjust(1, repeat=True)
    return markup.as_markup()


messages = {
    "uz": "🛒 Buyurtma berish",
    "ru": "🛒 Сделать заказ"
}


def order_inline(product_id: int, language: str):
    text = messages.get(language, messages["uz"])
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Buyurtma berish", callback_data=f"buy_{product_id}")]
        ]
    )
    return markup
