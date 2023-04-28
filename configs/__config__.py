from pymongo.collection import Collection
from pymongo.database import Database

from utils.configs import Config


def init(db: Database, config_file: str = None, config: Config = None) -> (Config, Collection):

    if config_file is not None:
        config = Config(config_file)

    settings: Collection = db[config['database']['settings']]
    result = settings.find_one({"key": "init"})
    if result is None:
        for key in config.data:
            if key != 'exclude' and key not in config['exclude']:
                settings.insert_one({
                    "user": 0,
                    "key": key,
                    "value": config[key]
                })
            elif key == 'personal':
                for user_id in config['personal']:
                    for pkey in config['personal'][user_id]:
                        settings.insert_one({
                            "user": user_id,
                            "key": pkey,
                            "value": config['personal'][user_id][pkey]
                        })

    else:
        params = settings.find({"user": 0})
        for res in params:
            config[res['key']] = res['value']

    return config, settings
