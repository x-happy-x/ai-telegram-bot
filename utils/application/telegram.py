import logging

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from configs import init
from utils import user as users
from utils.ai import ChatGPT, StableDiffusion
from utils.configs import *
from utils.database import Database


class TelegramBot:

    def __init__(self, **configs):
        # Connect logger
        logging.basicConfig(level=logging.INFO)
        self.logger = logging

        # Connect db
        self.db_config = DBConfig(configs['db'])
        self.db = Database(host=self.db_config['host'], port=self.db_config['port'])
        self.db_base = self.db[self.db_config['database']]

        # Connect storage
        self.storage = MemoryStorage()

        # Connect telegram
        self.bot_config = BotConfig(configs['bot'])
        self.bot = Bot(token=self.bot_config['token'], parse_mode="HTML")
        self.dp = Dispatcher(self.bot, storage=self.storage)

        # Connect ChatGPT
        try:
            self.gpt_config, self.gpt_settings = init(self.db_base, config=AIConfig(configs['gpt']))
            self.chat = ChatGPT(self.gpt_config, self.db_base)
        except pymongo.errors.ServerSelectionTimeoutError as e:
            self.log("Не удалось подключиться к базе данных\n:"+str(e))
            exit(1)

        # Connect StableDiffusion
        self.sd_config, self.sd_settings = init(self.db_base, config=AIConfig(configs['sd']))
        self.sd = StableDiffusion(self.sd_config, self.db_base)

        # Users configuration
        self.user_config, self.user_settings = init(self.db_base, config_file=configs['users'])
        users.init(self.user_config, self.db_base, [
            lambda x: self.chat.set_user_params(x)
        ])

    def log(self, message):
        self.logger.info(message)

    def start(self):
        executor.start_polling(self.dp)
        self.storage.close()
