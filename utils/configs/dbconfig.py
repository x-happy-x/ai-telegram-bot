from ..configs import Config


class DBConfig(Config):
    def get_config(self):
        return f"{self.configs_path}/{self.config_file}-db.json"
