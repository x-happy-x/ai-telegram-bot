import os
from dotenv import load_dotenv

load_dotenv()
ENV_OPTIONS = ['TELEGRAM_BOT_TOKEN', 'OPENAI_TOKEN', 'ALLOWED_USERS', 'MAX_HISTORY', 'ADMIN_USER_ID']


for file in os.listdir("./configs"):
    if file.endswith(".example"):
        os.rename(f"./configs/{file}", f"./configs/{file[:-8]}")
        file = file[:-8]
    with open(f"./configs/{file}", "r") as f:
        data = f.read()
    for option in ENV_OPTIONS:
        value = os.getenv(option)
        data = data.replace(option, value)
    with open(f"./configs/{file}", "w") as f:
        f.write(data)
