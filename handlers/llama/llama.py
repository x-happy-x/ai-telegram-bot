# Setting handlers
from aiogram.types import Message
from aiogram.utils.markdown import text

from utils import user as users
from utils.application import get_application

app = get_application()
help_message = text(
    "*LLaMA*",
    "\nПродолжение следует...",
    sep="\n"
)


@app.dp.message_handler(commands=["llama"])
async def start(message: Message):
    # logging
    app.log(message)
    # User & chat ids
    user_id, chat_id = users.get_info(message)
    # Select model
    app.select_model(user_id, chat_id, "llama")
    # Show message
    await message.answer("Выбрана нейросеть `LLaMA`.\n"
                         "Для всех последующих запросов она будет генерировать текстовые ответы.\n\n"
                         "Для того чтобы более подробно ознакомиться со всеми настройками "
                         "запустите команду /help", parse_mode="Markdown")


async def send_message(message: Message):
    await message.answer("*LLaMA временно недоступен, выберите другую модель*", parse_mode="Markdown")
