from os import getenv
from telegram.ext import Updater, CommandHandler, CallbackContext
import logging
import schedule
from requests import get
from story import Story, get_new_stories

# enables and get logger
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					 level=logging.INFO)
logger = logging.getLogger(__name__)

# fetching env variables
TOKEN = getenv("TELEGRAM_TOKEN")
JSON_URL = getenv("JSON_URL")
FETCH_INTERVAL = int(getenv("FETCH_INTERVAL", default=15)) # in minutes
CHAT_ID = getenv("CHAT_ID")

# save last story published
last_story = None

def start(update, context):
	"""
	Function handling the start of a conversation. it just send a welcome message
	"""
	update.message.reply_text("Ciao!")

def error(update, context):
	logger.warning('Update "%s" caused error "%s"', update, error)

# creating updater and getting dispatcher
updater = Updater(token = TOKEN, use_context = True) 
dispatcher = updater.dispatcher
job_queue = updater.job_queue

# adding handlers
dispatcher.add_error_handler(error)
dispatcher.add_handler(CommandHandler('start', start))

def publish_news(context: CallbackContext):
	global last_story
	response = get(JSON_URL)
	json = response.json()
	new_stories = get_new_stories(last_story, json)
	
	if (len(new_stories) == 0):
		logger.info("No new stories found since last check")
	else:
		last_story = new_stories[-1]
		for story in new_stories:
			context.bot.send_message(chat_id=CHAT_ID, text=f"{story.title}\n{story.url}")

job_minute = job_queue.run_repeating(publish_news, interval=FETCH_INTERVAL*60, first=0)

if __name__ == "__main__":
	updater.start_polling()