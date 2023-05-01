# Setting handlers
from aiogram import types
from aiogram.utils import exceptions
from aiogram.utils.markdown import text

from utils import user as users
from utils.application import get_application
from aiogram.utils.markdown import escape_md

app = get_application()

help_message = text(
    "*ChatGPT*\n",
    "Версия: `" + app.chat.model + "`",
    "\nДоступные команды:",
    "*/chatgpt_history_clear* - Очистка истории, ускорит обработку запроса и иногда избавляет от проблем с токенами",
    "*/set_max_history* - Установка макс. размера истории"
    "\nПродолжение следует...",
    sep="\n"
)


@app.dp.message_handler(commands=["chatgpt"])
async def start(message: types.Message):
    # logging
    app.log(message)
    # User & chat ids
    user_id, chat_id = users.get_info(message)
    # Select model
    users.select_model(user_id, chat_id, "chatgpt")
    # Show message
    await message.answer("Выбрана нейросеть `ChatGPT`.\n"
                         "Для всех последующих запросов она будет генерировать текстовые ответы.\n\n"
                         "Для того чтобы более подробно ознакомиться со всеми настройками "
                         "запустите команду /help", parse_mode="Markdown")


@app.dp.message_handler(commands=["chatgpt_history_clear"])
async def history_clear(message: types.Message):
    # logging
    app.log(message)
    # User & chat ids
    user_id, chat_id = users.get_info(message)
    # Get user
    user = users.get(user_id, chat_id)
    # Clear gpt history
    app.chat.clear_history(user)
    # Update user
    users.update(user_id, chat_id)
    # Show message
    await message.answer("История чата очищена")


@app.dp.message_handler(commands=["set_max_history"])
async def set_max_history(message: types.Message):
    # logging
    app.log(message)
    # User & chat ids
    user, chat = users.get_info(message)

    # Show message
    await message.answer(f"Test {user} {chat}")


async def send_message(message: types.Message):
    # User & chat ids
    user_id, chat_id = users.get_info(message)
    # Get user
    user = users.get(user_id, chat_id)
    # Send typing status
    await app.bot.send_chat_action(chat_id, types.ChatActions.TYPING)
    # Get an answer
    answer, usage = app.chat.generate(user, message.text)
    # Logging answer
    app.log(answer)
    # Update user
    users.update(user_id, chat_id)
    # Check answer
    try:
        if answer["role"] != "error":
            msg = "\n\n*Использование токенов:*\n" + \
                  f"Запросы: `{usage['prompt_tokens']}`\n" + \
                  f"Ответы: `{usage['completion_tokens']}`\n" + \
                  f"Всего: `{usage['total_tokens']}`\n\n" + \
                  f"*История сообщений: {usage['history']}*"
            msg_text = f"{answer['content']}{msg}"
            for x in range(0, len(msg_text), 4095):
                try:
                    try:
                        await message.answer(msg_text[x:x + 4095], parse_mode=types.ParseMode.MARKDOWN_V2)
                    except exceptions.CantParseEntities:
                        await message.answer(msg_text[x:x + 4095], parse_mode=types.ParseMode.MARKDOWN)
                except exceptions.CantParseEntities:
                    await message.answer(escape_md(msg_text[x:x + 4095]), parse_mode=types.ParseMode.MARKDOWN_V2)
        else:
            await message.answer("*Возникла проблема:* ```" + answer["content"] + "```", parse_mode=types.ParseMode.MARKDOWN_V2)
    except Exception as e:
        await message.answer("*Возникла проблема:* ```" + str(e) + "```", parse_mode=types.ParseMode.MARKDOWN_V2)
