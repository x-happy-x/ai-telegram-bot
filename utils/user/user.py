from aiogram import types
from pymongo.collection import Collection
from pymongo.database import Database

from utils.configs import Config


class User:
    config: Config
    settings: Collection
    messages: Collection
    users: Collection

    userdata: dict
    usermod: list


def init(self: Config, database: Database, usermod=None):
    if usermod is None:
        usermod = []
    User.config = self
    User.settings = database[self['database']['settings']]
    User.messages = database[self['database']['messages']]
    User.users = database[self['database']['users']]
    User.userdata = {}
    User.usermod = usermod


def create(user: int, chat: int):
    default_class = User.settings.find_one({"key": "class", "user": 0})["value"]
    class_user = User.settings.find_one({"key": "class", "user": user})
    if class_user is None:
        class_user = default_class
    else:
        class_user = class_user['value']
    user_profile = {
        "id": user,
        "chat": chat,
        "class": class_user,
        "mode": None
    }

    for user_id in User.config["personal"]:
        if int(user_id) == user:
            for pkey in User.config["personal"][user_id]:
                user_profile[pkey] = User.config["personal"][user_id][pkey]

    for modification in User.usermod:
        modification(user_profile)
    results = User.settings.find({"user": user})
    for r in results:
        user_profile[r["key"]] = r["value"]
    User.userdata[chat] = user_profile
    return user_profile


def update(user: int, chat: int):
    User.users.update_one({"id": user, "chat": chat}, {
        "$set": User.userdata[chat],
    })


def get(user: int, chat: int):
    # Find to bd
    result = User.users.find_one({"id": user, "chat": chat})

    # Find user or create
    if result is None:
        if chat not in User.userdata:
            create(user, chat)
        User.users.insert_one(User.userdata[chat])
    else:
        if chat not in User.userdata:
            User.userdata[chat] = result
        results = User.settings.find({"user": user})
        for r in results:
            User.userdata[chat][r["key"]] = r["value"]
        for user_id in User.config["personal"]:
            if int(user_id) == user:
                for pkey in User.config["personal"][user_id]:
                    User.userdata[chat][pkey] = User.config["personal"][user_id][pkey]
        update(user, chat)

    return User.userdata[chat]


def get_info(message: types.Message):
    user = message["from"]["id"]
    chat = message["chat"]["id"]
    return user, chat


def select_model(user, chat, model):
    result = get(user, chat)
    result["mode"] = model
    update(user, chat)
