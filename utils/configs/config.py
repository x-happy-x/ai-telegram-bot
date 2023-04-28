import json
import os


class Config:
    NO_VALUE = "no value"
    configs_path = "./configs"
    config_file = "config"
    data = {}

    def __init__(self, file=None) -> None:
        if file is not None:
            self.config_file = file
        if not os.path.exists(self.get_config()):
            return
        with open(self.get_config(), "r") as f:
            self.data = json.loads(f.read())

    def get_config(self):
        return f"{self.configs_path}/{self.config_file}.json"

    def __repr__(self) -> str:
        return "data:" + str(self.data)

    def __getitem__(self, i):
        try:
            return self.data[i]
        except KeyError:
            return self.NO_VALUE

    def __setitem__(self, key, value):
        self.data[key] = value

    def exists(self, i):
        return i in self.data.keys()

    def save(self):
        with open(self.get_config(), "w") as f:
            json.dump(self.data, f)
