from os import getenv

# Generic keys
FETCH_INTERVAL = int(getenv("FETCH_INTERVAL", default=15))
JSON_URL = getenv("JSON_URL")

# Twitter keys
CONSUMER_KEY = getenv("CONSUMER_KEY")
CONSUMER_SECRET = getenv("CONSUMER_SECRET")
ACCESS_TOKEN = getenv("ACCESS_TOKEN")
ACCESS_SECRET = getenv("ACCESS_SECRET")

# Telegram Keys
TOKEN = getenv("TELEGRAM_TOKEN")
CHAT_ID = getenv("CHAT_ID")

# Mastodon Keys

USERNAME = getenv("MASTODON_USERNAME")
PASSWORD = getenv("MASTODON_PASSWORD")
BASE_URL = getenv("MASTODON_BASE_URL")
