import logging
from datetime import datetime, timezone
from functools import partial
from traceback import print_exc
from os import getenv
import time
import schedule
from requests import get
from tweepy import OAuthHandler, API, TweepError
from twitter.twitter_utils import calc_expected_status_length

from story import Story, get_new_stories, StoryFormatter
from logging.config import fileConfig
import os.path
from config import LOGGING_CONF_FILE
from os import environ
import sentry_sdk

if 'SENTRY_URL' in environ:
    sentry_sdk.init(environ["SENTRY_URL"])

# enables and get logger
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					 level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_TWEET_LENGTH = 280
SHORT_URL_LENGTH = 23

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

TWITTER_PATTERN = "{title}\nLink: {story_url}\nCommenti: {discussion_url}\n{tags}"

class TwitterStoryFormatter(StoryFormatter):
    def __init__(self):
        super(TwitterStoryFormatter, self).__init__(
            pattern=TWITTER_PATTERN,
            story_preview_length_func=partial(calc_expected_status_length, short_url_length=SHORT_URL_LENGTH),
            max_length=MAX_TWEET_LENGTH
        )

def get_last_posted_tweet(bot: API) -> Story:
    """
    Gets the last tweet posted and parses it.

    :param bot: Twitter bot to fetch the tweet from.
    :return: Story parsed from the latest tweet posted.
    """
    # Gets its own Twitter ID
    twitter_id = bot.me().id
    # Gets its own last tweet
    last_tweet_list = bot.user_timeline(
        id=twitter_id, tweet_mode="extended", count=1)
    # If there are no valid tweets raises an exception
    if (len(last_tweet_list) == 0):
        raise ValueError("No valid tweet found")
    # Else gets latest tweet
    latest_tweet = last_tweet_list[0]
    # Injects UTC timezone into timestamp
    created_at = latest_tweet.created_at.replace(tzinfo=timezone.utc)
    # Parses tweet to retrieve required fields
    story = Story.from_string(pattern=TWITTER_PATTERN, string=latest_tweet.full_text, created_at=created_at)
    # Returns story
    return story

def main():
    # Creates bot
    bot = API(auth)
    logger.info("Checking for new posts...")
    # Fetches website to get new stories in JSON
    try:
        response = get(JSON_URL)
        json = response.json()
    except Exception as e:
        logger.error("Failed to connect to gambe.ro. Skipping.")
        return
    # Fetches Twitter for the last published stories
    last_posted_tweet = None
    new_stories = []
    try:
        last_posted_tweet = get_last_posted_tweet(bot)
        new_stories = get_new_stories(last_posted_tweet, json)
    # If is not possible to retrieve last tweet gets only the latest story on the website
    except ValueError:
        new_stories = [Story.from_json_dict(json[0])]
    # Tweets all the new stories
    if (len(new_stories) == 0):
        logger.info("Nothing new here, the bot is back to sleep.")
    else:
        for story in new_stories:
            tweet: str = None
            try:
                tweet = TwitterStoryFormatter().format_string(story)
                bot.update_status(tweet)
                logger.info(f"Tweeted: {tweet}")
            except ValueError:
                logger.critical("Unable to post tweet")
            except TweepError:
                print_exc()


if __name__ == "__main__":
    if os.path.isfile(LOGGING_CONF_FILE):
        fileConfig(LOGGING_CONF_FILE)
    main()
    schedule.every(FETCH_INTERVAL).minutes.do(main)
    while (True):
        schedule.run_pending()
        time.sleep(1000)
