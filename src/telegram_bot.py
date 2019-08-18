import logging
from datetime import date
from os import getenv, path
from requests import get
from telegram.ext import Updater, CommandHandler, CallbackContext
from story import Story, StoryFormatter, get_new_stories
from storage import Storage
#  enables and get logger
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
import os

# fetching env variables
TOKEN = getenv("TELEGRAM_TOKEN")
JSON_URL = getenv("JSON_URL")
FETCH_INTERVAL = int(getenv("FETCH_INTERVAL", 15))  # in minutes
CHAT_ID = getenv("CHAT_ID")
TELEGRAM_PATTERN = """**{title}** - {author}  
{tags}

[link]({story_url}) | [discussione]({discussion_url})
"""
class TelegramStorage(Storage):
    file_path = "/storage/telegram_bot_storage"

class TelegramStoryFormatter(StoryFormatter):
    def __init__(self):
        
        super(TelegramStoryFormatter, self).__init__(

            pattern=TELEGRAM_PATTERN,
            max_length=4096
        )


def get_latest_story(bot) -> Story:
    raise NotImplementedError()

def start(update, context):
    update.message.reply_text("Ciao!")


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, error)


def publish_news(context: CallbackContext):
    response = get(JSON_URL)
    json = response.json()

    storage = TelegramStorage()
    latest= storage.load()
    if latest:
        new_stories = get_new_stories(latest, json)
    else:
        new_stories = [Story.from_json_dict(json[0])]

    if len(new_stories) == 0:
        logger.info("No new stories found since last check")
    else:
        for story in new_stories:
            text = TelegramStoryFormatter(story).format_string()
            context.bot.send_message(chat_id=CHAT_ID, text=text)
        storage.save(new_stories[-1])

def main():
    # creating updater and getting dispatcher
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    job_queue = updater.job_queue

    #  adding handlers
    dispatcher.add_error_handler(error)
    dispatcher.add_handler(CommandHandler('start', start))

    job_queue.run_repeating(publish_news, interval=FETCH_INTERVAL * 60, first=0)

    updater.start_polling()


if __name__ == "__main__":
    main()
