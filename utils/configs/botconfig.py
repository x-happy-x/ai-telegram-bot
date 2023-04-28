from ..configs import Config


class BotConfig(Config):
    def get_config(self):
        return f"{self.configs_path}/{self.config_file}-bot.json"
