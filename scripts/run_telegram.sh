#! /usr/bin/bash
docker run  --mount type=bind,src=/storage,dst=/storage
    -e JSON_URL -e TELEGRAM_TOKEN -e CHAT_ID --entrypoint python telegram-twitter -u ./telegram_bot.py
