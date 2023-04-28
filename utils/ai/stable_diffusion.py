import webuiapi
from pymongo.database import Database
from requests.exceptions import ConnectionError
from webuiapi import WebUIApiResult

from utils.configs import AIConfig


class StableDiffusion:

    def __init__(self, config: AIConfig, database: Database):
        self.config = config
        self.api = webuiapi.WebUIApi(host=config['host'], port=config['port'])
        self.config = config

        self.commands = database[config['database']['commands']]
        self.settings = database[config['database']['settings']]

    def get_value(self, key: str) -> str | None:
        result = self.settings.find_one({"key": key})
        if result is not None:
            return result['value']
        return None

    def check(self, profile):
        # Access to stable diffusion
        if profile['class'] != 'admin':
            allowed = self.get_value("allowed_users")
            try:
                if allowed != "*":
                    allowed_list = list(map(int, allowed.split(",")))
                    allowed_list.index(profile["chat"])
            except ValueError:
                return False
        return True

    def send_request(self, profile, mode, **kwargs) -> WebUIApiResult | ConnectionError | TypeError | str:
        if self.check(profile):
            try:
                if mode == "img2img":
                    result = self.api.img2img(**kwargs)
                elif mode == "png_info":
                    result = self.api.png_info(**kwargs)
                else:
                    result = self.api.txt2img(**kwargs)
                info = result.info.copy()
                info["chat"] = profile["chat"]
                info["user"] = profile["id"]
                info["mode"] = mode
                self.commands.insert_one(info)
                return result
            except ConnectionError as e:
                return e
            except TypeError as e:
                return e
        else:
            return "Вы не имеете доступа к Stable Diffusion"
