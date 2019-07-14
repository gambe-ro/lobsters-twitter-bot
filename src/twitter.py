from os import getenv
from time import sleep
from datetime import datetime

from tweepy import OAuthHandler, API
from requests import get

import schedule

from story import Story, get_new_stories

# Maximum length
MAX_TWEET_LENGTH = 280

# Picks bot parameters from environment
CONSUMER_KEY = getenv("CONSUMER_KEY")
CONSUMER_SECRET = getenv("CONSUMER_SECRET")
ACCESS_TOKEN = getenv("ACCESS_TOKEN")
ACCESS_SECRET = getenv("ACCESS_SECRET")

JSON_URL = getenv("JSON_URL")

FETCH_INTERVAL = int(getenv("FETCH_INTERVAL", default=15))

# Authenticates to Twitter
auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)


def resize_tweet (string: str) -> str:
    """
    If string is bigger than the maximum tweet size, eliminates words to resize it.

    :param string: String to be prepared as a tweet.
    :return: String at least as long as the maximum tweet length.
    """
    # If tweet is shorter than limit, no need to resize
    if (len(string) <= MAX_TWEET_LENGTH):
        return string
    # Searches for the first space to terminate string
    i = MAX_TWEET_LENGTH - 1
    while ((string[i] != ' ') and (i >= 0)):
        i = i - 1
    # Returns terminated string
    return string[:i]

def get_last_posted_tweet(bot: API) -> Story:
    """
    Gets the last tweet posted and parses it.

    :param bot: Twitter bot to fetch the tweet from.  
    :return: Story parsed from the latest tweet posted.
    """
    # Gets its own Twitter ID
    twitter_id = bot.me().id
    # Gets its own last tweet
    latest_tweet = bot.user_timeline(
        id=twitter_id, tweet_mode="extended", count=1)[0]
    # Parses tweet to retrieve required fields
    story = Story.from_string(latest_tweet.full_text)
    return story


def main():
    # Creates bot
    bot = API(auth)
    print("Checking for new posts...")
    # Fetches Twitter for the last published stories
    last_posted_tweet = get_last_posted_tweet(bot)
    # Fetches website to get new stories in JSON
    response = get(JSON_URL)
    json = response.json()
    new_stories = get_new_stories(last_posted_tweet, json)
    # Tweets all the new stories
    print("[{time}]".format(time=datetime.now()), end=" ")
    if (len(new_stories) == 0):
        print("Nothing new here, the bot is back to sleep.")
    else:
        for story in new_stories:
            tweet = resize_tweet(story.__str__())
            bot.update_status(tweet)
            print(f"Tweeted: {tweet}")


if __name__ == "__main__":
    schedule.every(FETCH_INTERVAL).minutes.do(main)
    while (True):
        schedule.run_pending()