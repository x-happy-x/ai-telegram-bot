from utils.application import get_application
import asyncio

if __name__ == '__main__':
    print("Running")
    app = get_application(
        bot="telegram",
        gpt="chatgpt",
        sd="stable-diffusion",
        db="mongo",
        users="users")
    from handlers import import_var
    app.start()
    print("Stopped")
