from ..configs import Config


class AIConfig(Config):
    def get_config(self):
        return f"{self.configs_path}/{self.config_file}-ai.json"
