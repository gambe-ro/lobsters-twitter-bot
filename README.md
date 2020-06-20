# Lobste.rs bots

These bots have been created for [Gambe.ro](https://gambe.ro), the italian Lobsters fork. They fetch the newest stories from a Lobste.rs-compatible website and push them to various platforms (currently Twitter and Telegram).

## Configuring

Edit the `.env` file like this:

```
# URL to fetch JSON from (es. https://lobste.rs/newest.json)
JSON_URL=...
# Twitter app parameters
CONSUMER_KEY=...
CONSUMER_SECRET=...
ACCESS_TOKEN=...
ACCESS_SECRET=...
# Telegram bot parameters
TELEGRAM_TOKEN=...
CHAT_ID=...
# Interval (in minutes, optional, defaults to 15)
FETCH_INTERVAL=...
# Optional: a Sentry URL
SENTRY_URL=...
```

### Twitter

Go to [dev.twitter.com](https://dev.twitter.com) and create an Application that must be able to read and write tweets. Go to your app's page, in the "Keys and tokens" tab, then copy the parameters in `.env`.

### Telegram

Register a new bot with @BotFather, and get the chat ID for your group/channel with @get_id_bot.

## Running

To run the bot you need Docker and Docker Compose installed on your system. Once you have them, just:

```
$ git clone https://github.com/gambe-ro/lobsters-twitter-bot
$ docker-compose up
```

The bot is now up and running. Have fun!