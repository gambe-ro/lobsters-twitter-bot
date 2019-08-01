import logging
from os import getenv

from requests import get
from telegram.ext import Updater, CommandHandler, CallbackContext

from story import Story, get_new_stories, StoryPublishConfig

#  enables and get logger
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# fetching env variables
TOKEN = getenv("TELEGRAM_TOKEN")
JSON_URL = getenv("JSON_URL")
FETCH_INTERVAL = int(getenv("FETCH_INTERVAL", 15))  # in minutes
CHAT_ID = getenv("CHAT_ID")


class DefaultTelegramPublishConfig(StoryPublishConfig):
    def __init__(self):
        super(DefaultTelegramPublishConfig, self).__init__(
            len,
            max_length=500)

def start(update, context):
    """
    Function handling the start of a conversation. it just send a welcome message
    """
    update.message.reply_text("Ciao!")


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, error)


def publish_news(context: CallbackContext):
    last_story = context.job.context
    response = get(JSON_URL)
    json = response.json()

    new_stories = []
    if last_story is None:
        new_stories.append(Story.from_json_dict(json[0], DefaultTelegramPublishConfig()))
    else:
        try:
            new_stories = get_new_stories(last_story, json)
        except ValueError:
            new_stories.append(Story.from_json_dict(json[0], DefaultTelegramPublishConfig()))

    if len(new_stories) == 0:
        logger.info("No new stories found since last check")
    else:
        context.job.context = new_stories[-1]
        for story in new_stories:
            context.bot.send_message(chat_id=CHAT_ID, text=f"{story.title}\n{story.url}")


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
