from utils.application import get_application
import asyncio

if __name__ == '__main__':
    print("Sdasd")
    app = get_application(
        bot="test",
        gpt="gpt",
        sd="stable-diffusion",
        db="assistant",
        users="users")
    from handlers import import_var
    app.start()
    print("asdasd")
