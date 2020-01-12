from os import getenv

# Generic keys
FETCH_INTERVAL = int(getenv("FETCH_INTERVAL", default=15))
JSON_URL = getenv("JSON_URL","https://gambe.ro/newest.json")
LOGGING_CONF_FILE = getenv("LOGGING_CONF_FILE", default="logging.conf") #logging config file in python standard format

# Twitter keys
CONSUMER_KEY = getenv("CONSUMER_KEY")
CONSUMER_SECRET = getenv("CONSUMER_SECRET")
ACCESS_TOKEN = getenv("ACCESS_TOKEN")
ACCESS_SECRET = getenv("ACCESS_SECRET")

# Telegram Keys
TOKEN = getenv("TELEGRAM_TOKEN")
CHAT_ID = getenv("CHAT_ID")

# Mastodon Keys

USERNAME = getenv("PLEROMA_USERNAME")
PASSWORD = getenv("PLEROMA_PASSWORD")
BASE_URL = getenv("PLEROMA_BASE_URL")

# Linkedin Keys
LINKEDIN_KEY=getenv("LINKEDIN_KEY")
LINKEDIN_SECRET=getenv("LINKEDIN_SECRET")
LINKEDIN_TOKEN=getenv("LINKEDIN_TOKEN")