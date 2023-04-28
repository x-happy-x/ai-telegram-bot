from pymongo.database import Database

from ..configs.aiconfig import AIConfig


class ChatGPT:

    def __init__(self, config: AIConfig, database: Database):
        self.model = config['model']
        self.token = config['token']
        self.config = config

        # tables
        self.user_dialogs_table = database[config['database']['messages']]
        self.settings = database[config['database']['settings']]

        import openai
        openai.api_key = self.token
        self.generator = openai.ChatCompletion.create
        self.user_dialogs = {}

    def set_user_params(self, user: dict):
        user['role'] = self.get_value("role")
        user['max_history'] = int(self.get_value("default_max_history"))
        user['latest history'] = 0

    def get_value(self, key: str) -> str | None:
        result = self.settings.find_one({"key": key})
        if result is not None:
            return result['value']
        return None

    def generate(self, profile, message):
        user_id = 0
        default_mh = int(self.get_value("default_max_history"))
        max_history = default_mh
        if profile['class'] == 'admin':
            max_history = 100
        else:
            # Access to chatgpt
            allowed = self.get_value("allowed_users")
            try:
                if allowed != "*":
                    allowed_list = list(map(int, allowed.split(",")))
                    user_id = allowed_list.index(profile["chat"])
            except ValueError:
                return {
                    "role": "error",
                    "content": "Вы не имеете доступа к ChatGPT"
                }, None

            # max history size
            max_histories = self.get_value("max_history")
            try:
                if max_histories != "*":
                    max_histories_list = list(map(lambda x: x.strip(), max_histories.split(",")))
                    mh_id = 0
                    if len(max_histories_list) > user_id:
                        mh_id = user_id
                    max_history = int(max_histories_list[mh_id]) if max_histories_list[0].isnumeric() \
                        else default_mh
            except ValueError:
                max_history = default_mh
        # get last dialog
        if profile["chat"] not in self.user_dialogs:
            result = self.user_dialogs_table.find({"user": profile["chat"]}, limit=profile["latest history"])
            self.user_dialogs[profile["chat"]] = [r for r in result]
        # if dialog size big when max_history clear first messages
        while len(self.user_dialogs[profile["chat"]]) + 2 > max_history:
            self.user_dialogs[profile["chat"]].pop(0)
        # add a new message
        self.user_dialogs[profile["chat"]].append({
            "user": profile["chat"],
            "write": "user",
            "role": profile["role"],
            "content": message
        })
        # save history size
        profile["latest history"] = len(self.user_dialogs[profile["chat"]])
        # add a message to bd
        self.user_dialogs_table.insert_one(self.user_dialogs[profile["chat"]][-1])
        try:
            # generate answer
            result = self.generator(model=self.model, messages=[
                {
                    'role': msg['role'],
                    'content': msg['content']
                } for msg in self.user_dialogs[profile["chat"]]
            ])
            answer = result.choices[0].message
            # add answer to dialog
            self.user_dialogs[profile["chat"]].append({
                "user": result.id,
                "write": "ai",
                "role": answer.role,
                "content": answer.content
            })
            # save answer to bd
            self.user_dialogs_table.insert_one(self.user_dialogs[profile["chat"]][-1])
            # get stats
            usage = dict(result.usage)
            usage['history'] = len(self.user_dialogs[profile["chat"]])
            # save history size
            profile["latest history"] = len(self.user_dialogs[profile["chat"]])
            return dict(answer), usage
        except Exception as e:
            return {
                "role": "error",
                "content": str(e)
            }, None

    def clear_history(self, profile):
        self.user_dialogs[profile["chat"]] = []
        profile["latest history"] = 0
