# Setting handlers
import io

from PIL import Image
from aiogram.types import Message, MediaGroup, InputMediaPhoto, ChatActions
from aiogram.utils.markdown import text
from webuiapi import WebUIApiResult

from utils import user as users
from utils.application import get_application

app = get_application()

help_message = text(
    "*Stable Diffusion*",
    "\nПродолжение следует...",
    sep="\n"
)
help_message_img2img = text(
    "*Stable Diffusion*",
    "\nПродолжение следует...",
    sep="\n"
)
help_message_info = text(
    "*Stable Diffusion*",
    "\nПродолжение следует...",
    sep="\n"
)

help_message_txt2img = text("Значения по умолчанию:",
                            "enable_hr: bool = False",
                            "denoising_strength: float = 0.7,",
                            "firstphase_width: int = 0,",
                            "firstphase_height: int = 0,",
                            "hr_scale: int = 2,",
                            "hr_upscaler: HiResUpscaler = HiResUpscaler.Latent,",
                            "hr_second_pass_steps: int = 0,",
                            "hr_resize_x: int = 0,",
                            "hr_resize_y: int = 0,",
                            "prompt: str = "",",
                            "styles: list = [],",
                            "seed: int = -1,",
                            "subseed: int = -1,",
                            "subseed_strength: float = 0.0,",
                            "seed_resize_from_h: int = 0,",
                            "seed_resize_from_w: int = 0,",
                            "sampler_name: Any = None,",
                            "batch_size: int = 1,",
                            "n_iter: int = 1,",
                            "steps: Any = None,",
                            "cfg_scale: float = 7.0,",
                            "width: int = 512,",
                            "height: int = 512,",
                            "restore_faces: bool = False,",
                            "tiling: bool = False,",
                            "do_not_save_samples: bool = False,",
                            "do_not_save_grid: bool = False,",
                            "negative_prompt: str = "",",
                            "eta: float = 1.0,",
                            "s_churn: int = 0,",
                            "s_tmax: int = 0,",
                            "s_tmin: int = 0,",
                            "s_noise: int = 1,",
                            "override_settings: dict = {},",
                            "override_settings_restore_afterwards: bool = True,",
                            "script_args: Any = None,",
                            "script_name: Any = None,",
                            "send_images: bool = True,",
                            "save_images: bool = False,",
                            "alwayson_scripts: dict = {},",
                            "controlnet_units: list[ControlNetUnit] = [],",
                            "sampler_index: Any = None,",
                            "use_deprecated_controlnet: bool = False", sep="\n")


@app.dp.message_handler(commands=["stable_diffusion"])
async def start(message: Message):
    # logging
    app.log(message)
    # User & chat ids
    user_id, chat_id = users.get_info(message)
    # Select model
    users.select_model(user_id, chat_id, "sd")
    # Show message
    await message.answer("Выбрана нейросеть `Stable Diffusion`.\n"
                         "Для всех последующих запросов она будет генерировать изображения.\n\n"
                         "Для того чтобы более подробно ознакомиться со всеми настройками "
                         "запустите команду /help", parse_mode="Markdown")


async def send_message(message: Message):
    # User & chat ids
    user_id, chat_id = users.get_info(message)
    # Get user
    user = users.get(user_id, chat_id)
    # Send upload photo status
    await app.bot.send_chat_action(chat_id, ChatActions.UPLOAD_PHOTO)
    text = message.text if message.text is not None else message.caption if message.caption is not None else ""
    # Parse message
    args = {p[0].strip().lower(): p[1].strip() for p in
            filter(lambda p: len(p) == 2, [
                p.split(":", 1) for p in text.split("\n")
            ])}
    mode = "txt2img"
    if text.startswith("/img2img") or len(text) > 0 and len(message.photo) > 0:
        if text.startswith("/img2img help"):
            await app.bot.send_chat_action(chat_id, ChatActions.TYPING)
            await message.answer(help_message_img2img)
            return
        if len(message.photo) == 0:
            await app.bot.send_chat_action(chat_id, ChatActions.TYPING)
            await message.answer("Прикрепите изображение(ия) чтобы выполнить эту команду", parse_mode="Markdown")
            return
        mode = 'img2img'
        args['images'] = []
        bio = io.BytesIO()
        await message.photo[-1].download(destination_file=bio)
        image = Image.open(bio)
        args['images'].append(image)
        if 'styles' in args:
            args['styles'] = list(filter(lambda x: len(x) > 0, map(lambda x: x.strip(), args['styles'].split(","))))
    elif text.startswith("/info") or len(args) == 0 and len(message.photo) > 0:
        if text.startswith("/info help"):
            await app.bot.send_chat_action(chat_id, ChatActions.TYPING)
            await message.answer(help_message_info)
            return
        if len(message.photo) == 0:
            await app.bot.send_chat_action(chat_id, ChatActions.TYPING)
            await message.answer("Прикрепите изображение(ия) чтобы выполнить эту команду", parse_mode="Markdown")
            return
        mode = 'png_info'
        bio = io.BytesIO()
        await message.photo[-1].download(destination_file=bio)
        image = Image.open(bio)
        args['image'] = image
    else:
        if text.startswith("/txt2img help"):
            await app.bot.send_chat_action(chat_id, ChatActions.TYPING)
            await message.answer(help_message_txt2img)
            return
        if 'styles' in args:
            args['styles'] = list(filter(lambda x: len(x) > 0, map(lambda x: x.strip(), args['styles'].split(","))))

    # If not args, a message will be prompt
    if (len(args) == 0 or "prompt" not in args) and mode != "png_info":
        args["prompt"] = text.strip()

    result = app.sd.send_request(user, mode, **args)
    app.log(result)
    if isinstance(result, WebUIApiResult):
        media = MediaGroup()
        for image in result.images:
            bio = io.BytesIO()
            bio.name = 'image.png'
            image.save(bio, 'PNG')
            bio.seek(0)
            media.attach(InputMediaPhoto(bio))
        await message.answer_media_group(media)
    elif "got an unexpected keyword argument" in str(result):
        await message.answer(f"*Указаны не существующие параметры:*\n"
                             f"```{str(result).split('got an unexpected keyword argument')[-1].strip()}```",
                             parse_mode="Markdown")
    else:
        await message.answer("*Stable Diffusion временно недоступен*", parse_mode="Markdown")
