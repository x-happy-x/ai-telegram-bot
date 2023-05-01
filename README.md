# AI Assistant

Description...

## Usage

1. First, you need to run the database, for example in [docker](https://docs.docker.com/engine/install/):
   ```
   docker run --name assistant-db -p 27017:27017 -d mongo:latest
   ```
2. We are cloning this repository
   ```
   git clone https://github.com/x-happy-x/ai-telegram-bot.git
   cd ai-telegram-bot
   ```
3. Setting environment
   ```
   pip install poetry
   poetry install
   ```
4.

   1. Rename the configs so that they do not end with .example, but with .json at the end
      ```
      mv .\configs\telegram-bot.json.example .\configs\telegram-bot.json
      mv .\configs\chatgpt-ai.json.example .\configs\chatgpt-ai.json
      mv .\configs\stable-diffusion-ai.json.example .\configs\stable-diffusion-ai.json
      mv .\configs\mongo-db.json.example .\configs\mongo-db.json
      mv .\configs\users.json.example .\configs\users.json
      ```
      And manually open each config file, fill in the data between `*...*`,
      and the rest at your discretion.

   2. Or edit `.env` file and run:
      ```
      poetry run python configure.py
      ```
5. Launching the bot
   ```
   poetry run python main.py
   ```