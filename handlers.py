from aiogram import F, Router, Bot, types
from aiogram.types import Message
from aiogram.types import CallbackQuery
from buttons.inline import language_button, cat_inline, prod_inline, order_inline
from buttons.reply import get_menu, get_phone, check, menu, comp_ord, check_after_reg
import requests
from config import API, ADMIN
from aiogram.fsm.context import FSMContext
from states import SignupStates, OrderStates, CompleteOrderStates
from aiogram.types import ReplyKeyboardRemove
from decimal import Decimal
import json
from aiogram.filters import Command, CommandStart
from aiogram.enums import ParseMode

router = Router()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    try:
        await state.clear()
        response = requests.get(f"{API}/users/{message.from_user.id}")

        if response.status_code != 200:
            text = "Tilni tanlang 🇺🇿| Выберите язык 🇷🇺"
            await message.answer(text, reply_markup=language_button)
            return

        req = response.json()
        language = req.get("language", "uz")

        if not req["is_registered"]:
            full_name_prompt = {
                "uz": "👤 To‘liq ismingizni kiriting (F.I.Sh):",
                "ru": "👤 Введите ваше полное имя (Ф.И.О):"
            }
            txt = full_name_prompt.get(language, "Unknown language ❌")
            await message.answer(txt, reply_markup=ReplyKeyboardRemove())
            await state.set_state(SignupStates.name)
            return

        order_response = requests.get(f"{API}/user_orders/{req['id']}/")
        if order_response.status_code == 200 and order_response.json()['is_confirmed'] == False:
            order = order_response.json()
            requests.delete(f"{API}/order_del/{order['id']}/")

        services_text = {
            "uz": "💼 Bizning xizmatlar bilan tanishib chiqing\n\n💬 Yordam uchun: /help",
            "ru": "💼 Ознакомьтесь с нашими услугами\n\n💬 Для помощи используйте: /help"
        }
        txt = services_text.get(language, services_text["uz"])
        await message.answer(f"🌟 {message.from_user.full_name} {txt}", reply_markup=menu(language))
    except Exception as e:
        await message.answer(f"⚠️ So‘rovda xatolik: {e}")


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
async def stop_process(message: Message, state: FSMContext):
    try:
        response = requests.get(f"{API}/users/{message.from_user.id}")
        if response.status_code != 200:
            text = "Tilni tanlang 🇺🇿| Выберите язык 🇷🇺"
            await message.answer(text, reply_markup=language_button)
            return

        user = response.json()
        language = user.get("language", "uz")
        user_id = user["id"]

        order_response = requests.get(f"{API}/user_orders/{user_id}/")
        if order_response.status_code == 200 and order_response.json()['is_confirmed'] == False:
            order = order_response.json()
            requests.delete(f"{API}/order_del/{order['id']}/")

        current = await state.get_state()
        if current is None:
            no_data_text = {
                "uz": "🔍 To‘xtatish uchun ma'lumot mavjud emas",
                "ru": "🔍 Нет данных для остановки"
            }
            txt = no_data_text.get(language, no_data_text["uz"])
            await message.answer(txt, reply_markup=menu(language))
            return

        cancelled_text = {
            "uz": "❌ Jarayon bekor qilindi",
            "ru": "❌ Процесс был отменён"
        }
        txt = cancelled_text.get(language, cancelled_text["uz"])

        await message.answer(txt, reply_markup=menu(language))
        await state.clear()

    except Exception as e:
        await message.answer(f"⚠️ Xatolik yuz berdi: {e}")


@router.message(Command("new"))
async def restart_process(message: Message, state: FSMContext):
    try:
        response = requests.get(f"{API}/users/{message.from_user.id}")
        if response.status_code != 200:
            text = "Tilni tanlang 🇺🇿| Выберите язык 🇷🇺"
            await message.answer(text, reply_markup=language_button)
            return

        user = response.json()
        language = user.get("language", "uz")
        user_id = user["id"]

        order_response = requests.get(f"{API}/user_orders/{user_id}/")
        if order_response.status_code == 200 and order_response.json()['is_confirmed'] == False:
            order = order_response.json()
            requests.delete(f"{API}/order_del/{order['id']}/")

        await state.clear()

        if not user.get("is_registered", False):
            full_name_prompt = {
                "uz": "👤 To‘liq ismingizni kiriting (F.I.Sh):",
                "ru": "👤 Введите ваше полное имя (Ф.И.О):"
            }
            txt = full_name_prompt.get(language, full_name_prompt["uz"])
            await message.answer(txt, reply_markup=ReplyKeyboardRemove())
            await state.set_state(SignupStates.name)
            return

        already_registered_text = {
            "uz": f"✅ Siz ro‘yxatdan o‘tgansiz, {message.from_user.full_name}\n\n🚫 Sizda hech qanday buyurtma yo‘q.",
            "ru": f"✅ Вы уже зарегистрированы, {message.from_user.full_name}\n\n🚫 У вас нет активных заказов."
        }
        txt = already_registered_text.get(language, already_registered_text["uz"])

        await message.answer(txt, reply_markup=menu(language))

    except Exception as e:
        await message.answer(f"⚠️ Xatolik yuz berdi: {e}")


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
            "uz": "❗ Tasdiqlash yoki /new ni tanlang",
            "ru": "❗ Выберите Подтвердить или /new"
        }

        txt = messages.get(language, "Unknown language ❌")
        txt_conf = conf_msg.get(language, "Unknown language ❌")
        txt_template = templates.get(language, "Unknown language ❌")
        await message.answer(f"{txt}\n\n{txt_template}\n\n{txt_conf}", reply_markup=check(language))
        await state.set_state(SignupStates.check)

    else:
        await message.answer("❌ Send your contact information")


@router.message(SignupStates.check)
async def state_name(message: Message, state: FSMContext):
    req = requests.get(f"{API}/users/{message.from_user.id}").json()
    language = req["language"]
    if message.text in ["✅ Tasdiqlash", "✅ Подтвердить"]:
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
            await message.answer(text, reply_markup=check(language))
    else:
        txt = {
            "uz": (
                "✔️ Ma'lumotlarni tasdiqlash: Tasdiqlash\n"
                "🗑 Jarayonni bekor qilish: /stop\n"
                "🔄 Jarayonni boshidan boshlash: /new"
            ),
            "ru": (
                "✔️ Подтвердить информацию: Подтвердить\n"
                "🗑 Отменить процесс: /stop\n"
                "🔄 Начать процесс заново: /new"
            )
        }
        text = txt.get(language, txt["uz"])
        await message.answer(text, reply_markup=check(language))


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


@router.message(lambda msg: msg.text in ["🛒 Buyurtma berish", "🛒 Сделать заказ"])
async def register_button_handler(message: Message, state: FSMContext):
    await message.delete()
    try:
        response = requests.get(f"{API}/users/{message.from_user.id}")
        if response.status_code != 200:
            text = "Tilni tanlang 🇺🇿| Выберите язык 🇷🇺"
            await message.answer(text, reply_markup=language_button)
            return

        req = response.json()
        language = req.get("language", "uz")

        catgs = requests.get(f"{API}/cat_list/").json()

        if req["is_registered"] == False:
            full_name_prompt = {
                "uz": "👤 To‘liq ismingizni kiriting (F.I.Sh):",
                "ru": "👤 Введите ваше полное имя (Ф.И.О):"
            }
            txt = full_name_prompt.get(language, "Unknown language ❌")
            await message.answer(text=txt, reply_markup=ReplyKeyboardRemove())
            await state.set_state(SignupStates.name)
            return

        try:
            is_order = requests.get(url=f"{API}/user_orders/{req['id']}")
            if is_order.status_code == 404 and is_order.json()['is_confirmed'] == False:
                payload = {
                    "user": req['id'],
                }
                res_or_cre = requests.post(url=f"{API}/order_creat/", data=payload)
                if res_or_cre.status_code in [200, 201]:
                    messages = {
                        "uz": "📋 Kerakli bo‘limni tanlang",
                        "ru": "📋 Выберите нужный раздел"
                    }

                    mess = {
                        "uz": "📦 Buyurtma berish bo‘limi",
                        "ru": "📦 Раздел для оформления заказа"
                    }

                    tet = messages.get(language, "Unknown language ❌")
                    tgt = mess.get(language, "Unknown language ❌")
                    await message.answer(tgt, reply_markup=comp_ord(language))
                    await message.answer(tet, reply_markup=cat_inline(catgs))
                else:
                    return f"⚠️Error in the request: {res_or_cre.status_code} | {res_or_cre.text}"
            else:
                messages = {
                    "uz": "🟢 Sizda buyurtma ochilgan!",
                    "ru": "🟢 У вас открыт заказ!"
                }

                msgg = {
                    "uz": "📦 Savdoni davom ettirish uchun quyidagi bo‘limdan tanlang ⬇️\n\n❌ Jarayonni bekor qilish uchun: /stop ni bosing",
                    "ru": "📦 Чтобы продолжить покупку, выберите раздел ниже ⬇️\n\n❌ Чтобы отменить процесс, нажмите: /stop"
                }

                tet = messages.get(language, "Unknown language ❌")
                ttt = msgg.get(language, "Unknown language ❌")
                await message.answer(tet, reply_markup=comp_ord(language))
                await message.answer(ttt, reply_markup=cat_inline(catgs))
        except Exception as e:
            return f"[❌] Error in the request: {e}"
    except Exception as e:
        await message.answer(f"⚠️ So‘rovda xatolik: {e}", show_alert=True)


@router.callback_query(F.data.startswith("cat_"))
async def category_selected(callback: CallbackQuery, state):
    await callback.message.delete()
    try:
        response = requests.get(f"{API}/users/{callback.from_user.id}")
        if response.status_code != 200:
            text = "Tilni tanlang 🇺🇿| Выберите язык 🇷🇺"
            await callback.message.answer(text, reply_markup=language_button)
            return

        req = response.json()
        language = req.get("language", "uz")

        if not req.get("is_registered", False):
            full_name_prompt = {
                "uz": "👤 To‘liq ismingizni kiriting (F.I.Sh):",
                "ru": "👤 Введите ваше полное имя (Ф.И.О):"
            }
            txt = full_name_prompt.get(language, "Unknown language ❌")
            await callback.message.answer(text=txt, reply_markup=ReplyKeyboardRemove())
            await state.set_state(SignupStates.name)
            return

        category_id = int(callback.data.split("_")[1])

        product_response = requests.get(f"{API}/prod_categ/{category_id}/")

        if product_response.status_code != 200:
            messages = {
                "uz": "❌ Mahsulotlar topilmadi",
                "ru": "❌ Товары не найдены"
            }
            await callback.answer(messages.get(language, messages["uz"]), show_alert=True)
            return

        products = product_response.json()

        if not products:
            messages = {
                "uz": "❌ Bu kategoriyada mahsulot yo‘q",
                "ru": "❌ В этой категории нет товаров"
            }
            await callback.answer(messages.get(language, messages["uz"]), show_alert=True)
            return

        messages = {
            "uz": f"📦 {len(products)} ta mahsulot topildi:",
            "ru": f"📦 Найдено {len(products)} товаров:"
        }
        await callback.message.answer(
            text=messages.get(language, messages["uz"]),
            reply_markup=prod_inline(products, language, category_id)
        )

    except Exception as e:
        await callback.message.answer(f"⚠️ So‘rovda xatolik: {e}")


@router.callback_query(F.data.startswith("prod_"))
async def show_product_detail(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    product_id = int(callback.data.split("_")[1])

    try:
        response = requests.get(f"{API}/users/{callback.from_user.id}")
        if response.status_code != 200:
            text = "Tilni tanlang 🇺🇿| Выберите язык 🇷🇺"
            await callback.message.answer(text, reply_markup=language_button)
            return

        req = response.json()
        language = req.get("language", "uz")

        if req["is_registered"] == False:
            full_name_prompt = {
                "uz": "👤 To‘liq ismingizni kiriting (F.I.Sh):",
                "ru": "👤 Введите ваше полное имя (Ф.И.О):"
            }
            txt = full_name_prompt.get(language, "Unknown language ❌")
            await callback.message.answer(text=txt, reply_markup=ReplyKeyboardRemove())
            await state.set_state(SignupStates.name)
            return

        res = requests.get(f"{API}/products/{product_id}/")
        if res.status_code != 200:
            await callback.answer("❌ Mahsulot topilmadi", show_alert=True)
            return

        product = res.json()

        capt = {
            "uz": (
                f"<b>{product['name']}</b>\n"
                f"💰 Narxi: {product['price']} so‘m / {product['unit']}\n\n"
                f"📂 Kategoriya: {product['category_name']}\n"
                f"📦 Holati: {'Mavjud ✅' if product['available'] else 'Mavjud emas ❌'}"
            ),
            "ru": (
                f"<b>{product['name']}</b>\n"
                f"💰 Цена: {product['price']} сом / {product['unit']}\n\n"
                f"📂 Категория: {product['category_name']}\n"
                f"📦 Наличие: {'В наличии ✅' if product['available'] else 'Нет в наличии ❌'}"
            )
        }

        caption = capt.get(language, "Unknown language ❌")
        if product.get("photo"):
            await callback.message.answer_photo(
                photo=types.FSInputFile(product['photo']),
                caption=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=order_inline(product_id, language, product['category'])
            )
        else:
            await callback.message.answer(
                text=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=order_inline(product_id, language, product['category'])
            )
    except Exception as e:
        await callback.message.answer(f"⚠️ So‘rovda xatolik: {e}", show_alert=True)


@router.callback_query(F.data.startswith("buy_"))
async def ask_quantity(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[1])
    try:
        response = requests.get(f"{API}/users/{callback.from_user.id}")
        if response.status_code != 200:
            text = "Tilni tanlang 🇺🇿| Выберите язык 🇷🇺"
            await callback.message.answer(text, reply_markup=language_button)
            return

        req = response.json()
        language = req.get("language", "uz")

        if req["is_registered"] == False:
            full_name_prompt = {
                "uz": "👤 To‘liq ismingizni kiriting (F.I.Sh):",
                "ru": "👤 Введите ваше полное имя (Ф.И.О):"
            }
            txt = full_name_prompt.get(language, "Unknown language ❌")
            await callback.message.answer(text=txt, reply_markup=ReplyKeyboardRemove())
            await state.set_state(SignupStates.name)
            return

        is_order = requests.get(url=f"{API}/user_orders/{req['id']}")
        if is_order.status_code == 404:
            catgs = requests.get(f"{API}/cat_list/").json()
            payload = {
                "user": req['id'],
            }
            res_or_cre = requests.post(url=f"{API}/order_creat/", data=payload)
            if res_or_cre.status_code in [200, 201]:
                messages = {
                    "uz": "📋 Kerakli bo‘limni tanlang",
                    "ru": "📋 Выберите нужный раздел"
                }

                mess = {
                    "uz": "📦 Buyurtma berish bo‘limi",
                    "ru": "📦 Раздел для оформления заказа"
                }

                tet = messages.get(language, "Unknown language ❌")
                tgt = mess.get(language, "Unknown language ❌")
                await callback.message.answer(tgt, reply_markup=comp_ord(language))
                await callback.message.answer(tet, reply_markup=cat_inline(catgs))
            else:
                return f"⚠️Error in the request: {res_or_cre.status_code} | {res_or_cre.text}"
        else:
            await state.update_data(product_id=product_id)
            messages = {
                "uz": "✏️ Qancha hohlaysiz? (raqam kiriting)",
                "ru": "✏️ Сколько хотите? (введите число)"
            }
            caption = messages.get(language, "Unknown language ❌")
            await callback.message.answer(caption, reply_markup=comp_ord(language))
            await state.set_state(OrderStates.quantity)
    except Exception as e:
        await callback.message.answer(f"⚠️ So‘rovda xatolik: {e}", show_alert=True)


@router.message(OrderStates.quantity)
async def quantity_entered(message: Message, state: FSMContext):
    data = await state.get_data()
    product_id = data.get("product_id")

    try:
        quantity = float(message.text)
        if quantity <= 0.01:
            raise ValueError

        user_data = requests.get(f"{API}/users/{message.from_user.id}").json()
        user_order = requests.get(url=f"{API}/user_orders/{user_data['id']}").json()
        product = requests.get(f"{API}/products/{product_id}").json()
        catgs = requests.get(f"{API}/cat_list/").json()
        language = user_data.get("language", "uz")

        existing_item = next((item for item in user_order["items"] if item["product"] == product_id), None)

        if existing_item:
            item_id = existing_item["id"]
            new_quantity = Decimal(existing_item["quantity"]) + Decimal(str(quantity))
            payload = {
                "quantity": float(new_quantity)
            }
            update_or_it = requests.patch(f"{API}/orderit_update/{item_id}/", json=payload)
            if update_or_it.status_code in (200, 201):
                messages = {
                    "uz": f"✅ {quantity} ta '{product['name']}' mahsuloti savatga qo‘shildi!",
                    "ru": f"✅ {quantity} шт. товара '{product['name']}' добавлено в корзину!"
                }
                txt = messages.get(language, messages['uz'])
                await message.answer(txt, reply_markup=cat_inline(catgs))
            else:
                return f"⚠️Error in the request: {update_or_it.status_code} | {update_or_it.text}"
        else:
            payload = {
                "order": user_order["id"],
                "product": product_id,
                "quantity": float(quantity)
            }
            order_item_creat = requests.post(f"{API}/order_item_creat/", json=payload)
            if order_item_creat.status_code in [200, 201]:
                messages = {
                    "uz": f"✅ {quantity} ta '{product['name']}' mahsuloti savatga qo‘shildi!",
                    "ru": f"✅ {quantity} шт. товара '{product['name']}' добавлено в корзину!"
                }
                txt = messages.get(language, messages['uz'])
                await message.answer(txt, reply_markup=cat_inline(catgs))
            else:
                return f"⚠️Error in the request: {order_item_creat.status_code} | {order_item_creat.text}"

        await state.clear()
    except ValueError:
        messages = {
            "uz": "❌ Iltimos, miqdorni to‘g‘ri kiriting.",
            "ru": "❌ Пожалуйста, введите правильное количество."
        }
        txt = messages.get(language, messages['uz'])
        await message.answer(txt)


@router.callback_query(F.data.startswith("back_"))
async def back_handler(callback: CallbackQuery):
    await callback.message.delete()
    try:
        response = requests.get(f"{API}/users/{callback.from_user.id}")
        if response.status_code != 200:
            await callback.message.answer("Tilni tanlang 🇺🇿| Выберите язык 🇷🇺", reply_markup=language_button)
            return

        user = response.json()
        language = user.get("language", "uz")

        data = callback.data.split("_")

        if data[1] == "cat":
            catgs = requests.get(f"{API}/cat_list/").json()
            msg = {
                "uz": "📦 Kategoriyalar ro‘yxati:",
                "ru": "📦 Список категорий:"
            }
            await callback.message.answer(
                text=msg.get(language, msg["uz"]),
                reply_markup=cat_inline(catgs)
            )

        elif data[1] == "prod":
            category_id = int(data[2])
            product_response = requests.get(f"{API}/prod_categ/{category_id}/")
            if product_response.status_code != 200:
                messages = {
                    "uz": "❌ Mahsulotlar topilmadi",
                    "ru": "❌ Товары не найдены"
                }
                await callback.answer(messages.get(language, messages["uz"]), show_alert=True)
                return

            products = product_response.json()
            if not products:
                messages = {
                    "uz": "❌ Bu kategoriyada mahsulot yo‘q",
                    "ru": "❌ В этой категории нет товаров"
                }
                await callback.answer(messages.get(language, messages["uz"]), show_alert=True)
                return

            messages = {
                "uz": f"📦 {len(products)} ta mahsulot topildi:",
                "ru": f"📦 Найдено {len(products)} товаров:"
            }
            await callback.message.answer(
                text=messages.get(language, messages["uz"]),
                reply_markup=prod_inline(products, language, category_id)
            )

        else:
            await callback.answer("⚠️ Noma’lum orqaga tur!", show_alert=True)

    except Exception as e:
        await callback.message.answer(f"⚠️ So‘rovda xatolik: {e}")


# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
@router.message(F.text.in_(["✅ Buyurtmani yakunlash", "✅ Завершить заказ"]))
async def complete_order_start(message: Message, state: FSMContext):
    try:
        response = requests.get(f"{API}/users/{message.from_user.id}")
        catgs = requests.get(f"{API}/cat_list/").json()

        if response.status_code != 200:
            await message.answer("⚠️ Foydalanuvchi topilmadi")
            return

        user_data = response.json()
        language = user_data.get("language", "uz")
        user_id = user_data["id"]

        order_response = requests.get(f"{API}/user_orders/{user_id}/")

        if order_response.status_code != 200:
            await message.answer(
                "⚠️ Buyurtmalarni olishda xatolik yuz berdi" if language == "uz"
                else "⚠️ Ошибка при получении заказов"
            )
            return

        order = order_response.json()

        if not order or not order.get("items"):
            text = (
                "🛍 Sizda yakunlanmagan buyurtma mavjud emas.\nIltimos, avval mahsulot tanlang."
                if language == "uz"
                else "🛍 У вас нет активных заказов.\nПожалуйста, сначала выберите товары."
            )
            await message.answer(text, reply_markup=cat_inline(catgs))
            await state.clear()
            return

        delivery_address_text = {
            "uz": "📍 Yetkazib berish manzilini to‘liq kiriting:",
            "ru": "📍 Введите полный адрес доставки:"
        }

        await message.answer(delivery_address_text.get(language, delivery_address_text["uz"]),
                             reply_markup=ReplyKeyboardRemove())
        await state.set_state(CompleteOrderStates.address)

    except Exception as e:
        await message.answer(f"⚠️ Xatolik yuz berdi: {e}")


@router.message(CompleteOrderStates.address)
async def address_entered(message: Message, state: FSMContext):
    try:
        user = requests.get(f"{API}/users/{message.from_user.id}").json()
        language = user.get("language", "uz")
        address = message.text.strip()
        await state.update_data(address=address)

        order = requests.get(f"{API}/user_orders/{user['id']}/").json()
        items = order.get("items", [])

        grouped_items = {}
        for item in items:
            category = item["category_name"]
            if category not in grouped_items:
                grouped_items[category] = []
            grouped_items[category].append(item)

        receipt_lines = []
        for category, products in grouped_items.items():
            receipt_lines.append(f"📦 *{category}*")
            for item in products:
                name = item["product_name"]
                qty = float(item["quantity"])
                price = float(item["product_price"])
                total = float(item["total_price"])
                receipt_lines.append(f"• {name} — {qty} x {price:.2f} = {total:.2f}")
            receipt_lines.append("")

        items_text = "\n".join(receipt_lines)

        if language == "ru":
            text = (
                f"🧾 *Ваш заказ*\n\n"
                f"{items_text}\n"
                f"💰 *Итого:* {order['total_price']} сум\n\n"
                f"📍 Адрес: {address}\n\n"
                f"Проверьте данные и подтвердите заказ ✅\n\n\n"
                f"✔️ Подтвердить информацию: Подтвердить\n"
                f"🗑 Отменить процесс: /stop\n"
                f"🔄 Начать процесс заново: /start"
            )
        else:
            text = (
                f"🧾 *Sizning buyurtmangiz*\n\n"
                f"{items_text}\n"
                f"💰 *Jami:* {order['total_price']} so‘m\n\n"
                f"📍 Manzil: {address}\n\n"
                f"Ma’lumotlarni tekshirib, buyurtmani tasdiqlang ✅\n\n\n"
                f"✔️ Ma'lumotlarni tasdiqlash: Tasdiqlash\n"
                f"🗑 Jarayonni bekor qilish: /stop\n"
                f"🔄 Jarayonni boshidan boshlash: /start"
            )

        await message.answer(text, reply_markup=check_after_reg(language))
        await state.set_state(CompleteOrderStates.confirm_order)
    except Exception as e:
        await message.answer(f"⚠️ Xatolik yuz berdi: {e}")


@router.message(CompleteOrderStates.confirm_order)
async def confirm_order_state(message: Message, state: FSMContext):
    try:
        user = requests.get(f"{API}/users/{message.from_user.id}").json()
        language = user.get("language", "uz")

        if message.text in ["✅ Tasdiqlash", "✅ Подтвердить"]:
            order = requests.get(f"{API}/user_orders/{user['id']}/").json()
            items = order.get("items", [])

            data = await state.get_data()
            address = data.get("address", "Manzil kiritilmagan")

            grouped_items = {}
            for item in items:
                category = item["category_name"]
                grouped_items.setdefault(category, []).append(item)

            receipt_lines = []
            for category, products in grouped_items.items():
                receipt_lines.append(f"📦 *{category}*")
                for item in products:
                    name = item["product_name"]
                    qty = float(item["quantity"])
                    price = float(item["product_price"])
                    total = float(item["total_price"])
                    receipt_lines.append(f"• {name} — {qty} x {price:.2f} = {total:.2f}")
                receipt_lines.append("")

            items_text = "\n".join(receipt_lines)

            try:
                update = requests.patch(
                    f"{API}/user_order_update/{user['id']}/",
                    json={"is_confirmed": True}
                )
                if update.status_code not in [200, 201]:
                    await message.answer(f"⚠️ Buyurtma berilmadi: {update.text}")
                    return
            except Exception as e:
                await message.answer(f"⚠️ Xatolik yuz berdi (update): {e}", reply_markup=menu(language))
                return

            admin_text = (
                f"📩 *Yangi buyurtma*\n\n"
                f"{items_text}\n"
                f"💰 *Jami:* {order['total_price']} so‘m\n"
                f"📍 Manzil: {address}\n\n"
                f"👤 Foydalanuvchi: {user.get('first_name', '')} (@{user.get('user_name', '')})\n"
                f"📞 Telefon: {user.get('phone_number', '❌ Telefon yo‘q')}"
            )

            admin = requests.get(f"{API}/users/{ADMIN}").json()
            if language == "ru":
                user_text = (
                    f"✅ Ваши данные были отправлены администратору!\n"
                    f"📩 Связаться с администратором: [@{admin['user_name']}](https://t.me/{admin['user_name']})\n\n"
                    f"🔁 Хотите сделать новый заказ?"
                )
            else:
                user_text = (
                    f"✅ Ma’lumotlaringiz adminga yuborildi!\n"
                    f"📩 Admin bilan bog‘lanish: [@{admin['user_name']}](https://t.me/{admin['user_name']})\n\n"
                    f"🔁 Qayta buyurtma bermoqchimisiz?"
                )

            await message.bot.send_message(
                ADMIN, admin_text, parse_mode="HTML", disable_web_page_preview=True
            )

            await message.answer(user_text, reply_markup=menu(language))
            await state.clear()
        else:
            txt = {
                "uz": (
                    "✔️ Ma'lumotlarni tasdiqlash: Tasdiqlash\n"
                    "🗑 Jarayonni bekor qilish: /stop\n"
                    "🔄 Jarayonni boshidan boshlash: /start"
                ),
                "ru": (
                    "✔️ Подтвердить информацию: Подтвердить\n"
                    "🗑 Отменить процесс: /stop\n"
                    "🔄 Начать процесс заново: /start"
                )
            }
            text = txt.get(language, txt["uz"])
            await message.answer(text, reply_markup=check_after_reg(language))
    except Exception as e:
        await message.answer(f"⚠️ Xatolik yuz berdi: {e}")
