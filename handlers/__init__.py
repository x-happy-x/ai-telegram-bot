from aiogram import types
from aiogram.types import ContentType

from utils import user as users
from utils.application import get_application
from .chatgpt import send_message as chatgpt_send_message, help_message as chatgpt_help_message
from .llama import send_message as llama_send_message, help_message as llama_help_message
from .stable_diffusion import send_message as sd_send_message, help_message as sd_help_message

app = get_application()


@app.dp.message_handler(commands=["test"])
async def all_messages(message: types.Message):
    # logging
    app.log(message)

    button_hi = types.KeyboardButton('Привет! 👋')

    greet_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    greet_kb.add(button_hi, )


@app.dp.message_handler(commands=["help", "options"])
async def help_message(message: types.Message):
    # logging
    app.log(message)
    # User & chat ids
    user_id, chat_id = users.get_info(message)
    # Get user
    user = users.get(user_id, chat_id)
    # help command
    if message.text == "/help":
        await message.answer(globals()[user["mode"] + "_help_message"], parse_mode="Markdown")
    else:
        await message.answer("Пока не готово")


@app.dp.message_handler(content_types=ContentType.PHOTO)
async def get_image(message: types.Message):
    # logging
    app.log(message)
    # User & chat ids
    user_id, chat_id = users.get_info(message)
    # Get user
    user = users.get(user_id, chat_id)
    # Check selected mode
    if user['mode'] is None:
        await message.answer("Выберите действие из меню")
    if user['mode'] == "sd":
        await globals()[user["mode"] + "_send_message"](message)
    else:
        await message.answer("В этом режиме отправка фото не поддерживается")
        # await globals()[user["mode"] + "_send_message"](message)


@app.dp.message_handler()
async def send_message(message: types.Message):
    # logging
    app.log(message)
    # User & chat ids
    user_id, chat_id = users.get_info(message)
    # Get user
    user = users.get(user_id, chat_id)
    # Check selected mode
    if user['mode'] is None:
        await message.answer("Выберите действие из меню")
    else:
        await globals()[user["mode"] + "_send_message"](message)


import_var = None
