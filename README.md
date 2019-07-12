# Lobste.rs Twitter Bot

This bot has been created for [Gambe.ro](https://gambe.ro), the italian Lobsters fork, and tweets the newest story posted on every Lobste.rs-compatible website that exposes at least a JSON page.

The first thing you need to run the bot it's to go to [dev.twitter.com](https://dev.twitter.com) and create an Application, that must be able to Read and Write tweets. Go to your app's page, in the "Keys and tokens" tab, then copy the parameters you see in `.env`, as follows.

```
cat .env << STOP
# URL to fetch JSON from (es. https://lobste.rs/newest.json)
JSON_URL=...
# Twitter app parameters
CONSUMER_KEY=...
CONSUMER_SECRET=...
ACCESS_TOKEN=...
ACCESS_SECRET=...
# Interval (in minutes, optional, defaults to 15)
FETCH_INTERVAL=...
STOP
```

To run the bot you need Docker and Docker Compose installed on your system. Once you have them, just:

```
$ git clone https://github.com/gambe-ro/lobsters-twitter-bot
$ docker-compose up
```

The bot is now up and running. Have fun!