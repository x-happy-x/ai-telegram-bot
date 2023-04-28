from .telegram import TelegramBot

instance = None


def get_application(**configs):
    global instance
    if instance is None:
        instance = TelegramBot(**configs)
    return instance
