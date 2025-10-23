from aiogram import F, Router, Bot
from aiogram.types import Message
from aiogram.types import CallbackQuery
from buttons.inline import language_button
from buttons.reply import get_menu, get_phone, check, menu
import requests
from config import API, ADMIN
from aiogram.fsm.context import FSMContext
from states import SignupStates
from aiogram.types import ReplyKeyboardRemove
import json
import qrcode
import os
from aiogram.types import FSInputFile
from aiogram.filters import Command, CommandStart

router = Router()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    try:
        response = requests.get(f"{API}/users/{message.from_user.id}")
        if response.status_code != 200:
            text = "Tilni tanlang 🇺🇿| Выберите язык 🇷🇺"
            await message.answer(text, reply_markup=language_button)
            return

        req = response.json()
        language = req.get("language", "uz")

        if req["is_registered"] == False:
            full_name_prompt = {
                "uz": "👤 To‘liq ismingizni kiriting (F.I.Sh):",
                "ru": "👤 Введите ваше полное имя (Ф.И.О):"
            }
            txt = full_name_prompt.get(language, "Unknown language ❌")
            await message.answer(text=txt, reply_markup=ReplyKeyboardRemove())
            await state.set_state(SignupStates.name)
            return

        services_text = {
            "uz": "Bizning xizmatlar bilan tanishib chiqing",
            "ru": "Ознакомьтесь с нашими услугами"
        }
        txt = services_text.get(language, services_text["uz"])
        await message.answer(f"🌟 {message.from_user.full_name}  {txt}", reply_markup=menu(language))
    except Exception as e:
        await message.answer(f"⚠️ So‘rovda xatolik: {e}", show_alert=True)


@router.message(Command("help"))
async def state_name(message: Message, state: FSMContext):
    try:
        response = requests.get(f"{API}/users/{message.from_user.id}")
        if response.status_code != 200:
            text = "Tilni tanlang 🇺🇿| Выберите язык 🇷🇺"
            await message.answer(text, reply_markup=language_button)
            return

        req = response.json()
        language = req.get("language", "uz")

        if req["is_registered"] == False:
            full_name_prompt = {
                "uz": "👤 To‘liq ismingizni kiriting (F.I.Sh):",
                "ru": "👤 Введите ваше полное имя (Ф.И.О):"
            }
            txt = full_name_prompt.get(language, "Unknown language ❌")
            await message.answer(text=txt, reply_markup=ReplyKeyboardRemove())
            await state.set_state(SignupStates.name)
            return

        res = requests.get(f"{API}/users/{ADMIN}").json()

        help_text = {
            "uz": "👨🏻‍💻 Yordam uchun Adminga murojaat qiling",
            "ru": "👨🏻‍💻 Для помощи обратитесь к Администратору"
        }
        txt = help_text.get(language, "Unknown language ❌")
        await message.answer(
            f"{txt}\n\nhttps://t.me/{res['user_name']}", reply_markup=menu(language))
    except Exception as e:
        await message.answer(f"⚠️ So‘rovda xatolik: {e}", show_alert=True)


@router.callback_query(lambda c: c.data.startswith("stlang_"))
async def process_language(callback: CallbackQuery):
    await callback.message.delete()
    lang_code = callback.data.split("_")[1]
    user_id = callback.from_user.id
    try:
        response = requests.get(f"{API}/users/{user_id}")
        if response.status_code != 200:
            payload = {
                "telegram_id": user_id,
                "user_name": callback.from_user.username,
                "language": lang_code,
            }
            try:
                response = requests.post(url=f"{API}/create_user/", data=payload)
                if response.status_code in [200, 201]:
                    msg = {
                        "uz": "✅ Siz O‘zbek tilini tanladingiz 🇺🇿",
                        "ru": "✅ Вы выбрали Русский 🇷🇺"
                    }

                    register_to_use_bot_text = {
                        "uz": "🤖 Botdan foydalanish uchun ro‘yxatdan o‘ting",
                        "ru": "🤖 Чтобы использовать бота, пожалуйста, зарегистрируйтесь"
                    }

                    tet = msg.get(lang_code, "Unknown language ❌")
                    text = register_to_use_bot_text.get(lang_code, "Unknown language ❌")
                    await callback.message.answer(f"{tet}\n\n{text}", reply_markup=get_menu(lang_code))
                    return
                else:
                    return f"⚠️Error in the request: {response.status_code} | {response.text}"
            except Exception as e:
                return f"[❌] Error in the request: {e}"

        req = response.json()
        language = req.get("language", "uz")

        if req["is_registered"] == False:
            full_name_prompt = {
                "uz": "👤 To‘liq ismingizni kiriting (F.I.Sh):",
                "ru": "👤 Введите ваше полное имя (Ф.И.О):"
            }
            txt = full_name_prompt.get(language, "Unknown language ❌")
            await callback.message.answer(text=txt, reply_markup=ReplyKeyboardRemove())
            await callback.state.set_state(SignupStates.name)
            return

        payload = {
            "language": lang_code,
        }
        try:
            response = requests.patch(url=f"{API}/user_update/{user_id}/", json=payload)
            if response.status_code in [200, 201]:
                messages = {
                    "uz": "✅ Siz O‘zbek tilini tanladingiz 🇺🇿",
                    "ru": "✅ Вы выбрали Русский 🇷🇺"
                }
                text = messages.get(lang_code, "Unknown language ❌")
                await callback.message.answer(text, reply_markup=menu(lang_code))
            else:
                return f"⚠️Error in the request: {response.status_code} | {response.text}"
        except Exception as e:
            return f"[❌] Error in the request: {e}"

        await callback.answer()
    except Exception as e:
        await callback.message.answer(f"⚠️ Error in the request: {e}", show_alert=True)


@router.message(lambda msg: msg.text in ["📝 Ro'yhatdan o'tish", "📝 Регистрация"])
async def register_button_handler(message: Message, state: FSMContext):
    try:
        response = requests.get(f"{API}/users/{message.from_user.id}")
        if response.status_code != 200:
            text = "Tilni tanlang 🇺🇿| Выберите язык 🇷🇺"
            await message.answer(text, reply_markup=language_button)
            return
        req = response.json()
        language = req.get("language", "uz")

        if req["is_registered"] == False:
            full_name_prompt = {
                "uz": "👤 To‘liq ismingizni kiriting (F.I.Sh):",
                "ru": "👤 Введите ваше полное имя (Ф.И.О):"
            }
            txt = full_name_prompt.get(language, "Unknown language ❌")
            await message.answer(text=txt, reply_markup=ReplyKeyboardRemove())
            await state.set_state(SignupStates.name)
            return

        services_text = {
            "uz": "Bizning xizmatlar bilan tanishib chiqing",
            "ru": "Ознакомьтесь с нашими услугами"
        }
        txt = services_text.get(language, services_text["uz"])
        await message.answer(f"🌟 {message.from_user.full_name}  {txt}", reply_markup=menu(language))

    except Exception as e:
        await message.answer(f"⚠️ Error in the request: {e}", show_alert=True)


@router.message(Command("stop"))
async def state_name(message: Message, state: FSMContext):
    try:
        response = requests.get(f"{API}/users/{message.from_user.id}")
        if response.status_code != 200:
            text = "Tilni tanlang 🇺🇿| Выберите язык 🇷🇺"
            await message.answer(text, reply_markup=language_button)
            return
        req = response.json()
        language = req.get("language", "uz")

        curent = await state.get_state()
        if curent == None:
            no_data_text = {
                "uz": "🔍 To'xtatish uchun ma'lumot mavjud emas",
                "ru": "🔍 Нет данных для остановки"
            }
            txt = no_data_text.get(language, "Unknown language ❌")
            await message.answer(txt)
        else:
            cancelled_text = {
                "uz": "❌ Jarayon bekor qilindi",
                "ru": "❌ Процесс был отменён"
            }
            txt = cancelled_text.get(language, "Unknown language ❌")
            await message.answer(txt)
            await state.clear()
    except Exception as e:
        await message.answer(f"⚠️ Error in the request: {e}", show_alert=True)


@router.message(Command("new"))
async def state_name(message: Message, state: FSMContext):
    curent = await state.get_state()
    try:
        response = requests.get(f"{API}/users/{message.from_user.id}")
        if response.status_code != 200:
            text = "Tilni tanlang 🇺🇿| Выберите язык 🇷🇺"
            await message.answer(text, reply_markup=language_button)
            return
        req = response.json()
        language = req.get("language", "uz")

        if req["is_registered"] == False:
            full_name_prompt = {
                "uz": "👤 To‘liq ismingizni kiriting (F.I.Sh):",
                "ru": "👤 Введите ваше полное имя (Ф.И.О):"
            }
            txt = full_name_prompt.get(language, "Unknown language ❌")

            if curent == None:
                await message.answer(text=txt, reply_markup=ReplyKeyboardRemove())
                await state.set_state(SignupStates.name)
                return
            else:
                await state.clear()
                await message.answer(text=txt, reply_markup=ReplyKeyboardRemove())
                await state.set_state(SignupStates.name)
                return
        else:
            already_registered_text = {
                "uz": "✅ Siz ro‘yxatdan o‘tgansiz",
                "ru": "✅ Вы уже зарегистрированы"
            }

            txt = already_registered_text.get(language, already_registered_text["uz"])
            await message.answer(f"{message.from_user.full_name}  {txt}", reply_markup=menu(language))
    except Exception as e:
        await message.answer(f"⚠️ Error in the request: {e}", show_alert=True)


# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

@router.message(SignupStates.name)
async def state_name(message: Message, state: FSMContext):
    res = requests.get(f"{API}/users/{message.from_user.id}").json()
    language = res["language"]
    if 4 <= len(message.text) <= 100:
        if not any(digit in message.text for digit in '0123456789'):
            await state.update_data(name=message.text)
            accepted_message = {
                "uz": "✅ Qabul qilindi",
                "ru": "✅ Принято"
            }
            age_prompt = {
                "uz": "📅 Yoshingizni kiriting",
                "ru": "📅 Введите ваш возраст"
            }
            txt_acc = accepted_message.get(language, "Unknown language ❌")
            txt_age = age_prompt.get(language, "Unknown language ❌")
            await message.answer(f"{txt_acc}\n\n👤 {message.text}")
            await message.answer(txt_age)
            await state.set_state(SignupStates.age)
        else:
            await message.answer("❌ The name cannot contain numbers!")
    else:
        await message.answer("❌ The length of the information you entered is invalid!")


@router.message(SignupStates.age)
async def state_age(message: Message, state: FSMContext):
    res = requests.get(f"{API}/users/{message.from_user.id}").json()
    language = res["language"]
    if message.text.isdigit() and 4 < int(message.text) < 50:
        await state.update_data(age=message.text)
        accepted_message = {
            "uz": "✅ Qabul qilindi",
            "ru": "✅ Принято"
        }
        phone_prompt = {
            "uz": "📞 Telefon raqamingizni jo‘nating",
            "ru": "📞 Отправьте свой номер телефона"
        }
        txt_acc = accepted_message.get(language, "Unknown language ❌")
        txt_phone = phone_prompt.get(language, "Unknown language ❌")
        await message.answer(f"{txt_acc}\n\n📅 {message.text}")
        await message.answer(txt_phone,
                             reply_markup=get_phone(language))
        await state.set_state(SignupStates.phone)
    else:
        await message.answer("❌ Enter a valid age (between 4 and 50)")


@router.message(SignupStates.phone)
async def state_phone(message: Message, state: FSMContext):
    res = requests.get(f"{API}/users/{message.from_user.id}").json()
    language = res["language"]
    if message.contact:
        await state.update_data(phone=message.contact.phone_number)
        accepted_message = {
            "uz": "✅ Qabul qilindi",
            "ru": "✅ Принято"
        }

        txt_acc = accepted_message.get(language, "Unknown language ❌")
        await message.answer(f"{txt_acc}\n\n📞 {message.contact.phone_number}")
        data = await state.get_data()
        templates = {
            "uz": (
                f"Ariza Beruvchi: {data.get('name')}\n"
                f"Yoshingiz: {data.get('age')}\n"
                f"User name: @{message.from_user.username}\n"
                f"Telefon raqamingiz: {data.get('phone')}\n"
            ),
            "ru": (
                f"Заявитель: {data.get('name')}\n"
                f"Возраст: {data.get('age')}\n"
                f"Имя пользователя: @{message.from_user.username}\n"
                f"Телефон: {data.get('phone')}\n"
            )
        }

        messages = {
            "uz": "✅ Ma'lumotlarni tasdiqlaysizmi?",
            "ru": "✅ Вы подтверждаете данные?"
        }

        conf_msg = {
            "uz": "❗ ✔️ yoki /new ni tanlang",
            "ru": "❗ Выберите ✔️ или /new"
        }

        txt = messages.get(language, "Unknown language ❌")
        txt_conf = conf_msg.get(language, "Unknown language ❌")
        txt_template = templates.get(language, "Unknown language ❌")
        await message.answer(f"{txt}\n\n{txt_template}\n\n{txt_conf}", reply_markup=check)
        await state.set_state(SignupStates.check)

    else:
        await message.answer("❌ Send your contact information")


@router.message(SignupStates.check)
async def state_name(message: Message, state: FSMContext, bot: Bot):
    req = requests.get(f"{API}/users/{message.from_user.id}").json()
    language = req["language"]
    if message.text == "✔️":
        data = await state.get_data()

        api_data = {
            'first_name': data.get('name'),
            'age': data.get('age'),
            'phone_number': data.get('phone'),
            'is_registered': True
        }

        postResponse = requests.patch(url=f"{API}/user_update/{message.from_user.id}/", json=api_data)

        if postResponse.status_code in (200, 201):
            json.dumps(postResponse.json(), indent=4)
            messages = {
                "uz": "✅ Arizangiz qabul qilindi",
                "ru": "✅ Ваша заявка принята"
            }
            txt = messages.get(language, "Unknown language ❌")
            await message.answer(txt, reply_markup=menu(language))
            await state.clear()

        else:
            error_text = {
                "uz": (
                    "❌ Ma'lumotlaringiz saqlanmadi\n\n"
                    "🗑 Jarayonni bekor qilish: /stop\n"
                    "🔄 Jarayonni boshidan boshlash: /new"
                ),
                "ru": (
                    "❌ Ваши данные не сохранены\n\n"
                    "🗑 Отменить процесс: /stop\n"
                    "🔄 Начать процесс заново: /new"
                )
            }
            text = error_text.get(language, error_text["uz"])
            await message.answer(text, reply_markup=check)
    else:
        txt = {
            "uz": (
                "✔️ Ma'lumotlarni tasdiqlash: Ha\n"
                "🗑 Jarayonni bekor qilish: /stop\n"
                "🔄 Jarayonni boshidan boshlash: /new"
            ),
            "ru": (
                "✔️ Подтвердить информацию: Да\n"
                "🗑 Отменить процесс: /stop\n"
                "🔄 Начать процесс заново: /new"
            )
        }
        text = txt.get(language, txt["uz"])
        await message.answer(txt, reply_markup=check)


# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
@router.message(lambda msg: msg.text in ["🌐 Tilni o‘zgartirish", "🌐 Change language", "🌐 Изменить язык"])
async def register_button_handler(message: Message, state: FSMContext):
    try:
        response = requests.get(f"{API}/users/{message.from_user.id}")
        if response.status_code != 200:
            text = "Tilni tanlang 🇺🇿| Выберите язык 🇷🇺"
            await message.answer(text, reply_markup=language_button)
            return

        req = response.json()
        language = req.get("language", "uz")

        if req["is_registered"] == False:
            full_name_prompt = {
                "uz": "👤 To‘liq ismingizni kiriting (F.I.Sh):",
                "ru": "👤 Введите ваше полное имя (Ф.И.О):"
            }
            txt = full_name_prompt.get(language, "Unknown language ❌")
            await message.answer(text=txt, reply_markup=ReplyKeyboardRemove())
            await state.set_state(SignupStates.name)
            return

        text = "Tilni tanlang 🇺🇿| Выберите язык 🇷🇺"
        await message.answer(text, reply_markup=language_button)
    except Exception as e:
        await message.answer(f"⚠️ So‘rovda xatolik: {e}", show_alert=True)


@router.message(lambda msg: msg.text in ["📝 Ruhsatnoma olish", "📝 Получить разрешение"])
async def register_button_handler(message: Message):
    pass
