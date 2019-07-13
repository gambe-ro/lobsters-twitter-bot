from os import getenv
from time import sleep

from tweepy import OAuthHandler, API
from requests import get

from parse import parse

import schedule

# Picks bot parameters from environment
CONSUMER_KEY = getenv("CONSUMER_KEY")
CONSUMER_SECRET = getenv("CONSUMER_SECRET")
ACCESS_TOKEN = getenv("ACCESS_TOKEN")
ACCESS_SECRET = getenv("ACCESS_SECRET")

JSON_URL = getenv("JSON_URL")

FETCH_INTERVAL = int(getenv("FETCH_INTERVAL", default=15))

# Tweet format
TWEET_FORMAT = "{title} - {short_id_url} ({author}, {created_at}) {hashtags}"

# Authenticates to Twitter
auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

def get_newest_story () -> dict:
    """
    Gets the newest story posted on the site.

    :return: Dictionary with data of the newest story in the JSON.
    """
    # Gets the webpage
    request = get(JSON_URL)
    # Extrapolates JSON content
    json_result = request.json()
    # Gets first element
    story = json_result[0]
    # Modifies internal structure to facilitate parsing
    story["author"] = story["submitter_user"]["username"]
    # Returns the story
    return story

def is_newest (story_a: dict, story_b: dict) -> bool:
    """
    Returns True if the first story is newest than the second one.

    :param story_a: Story to be verified as newest.
    :param story_b: Other story to be compared.
    :return: True if story_a is newest than story_b, False otherwise.
    """
    # If there is no second story, first is newest.
    if (story_b is None):
        return True
    # If created_at fields are different, first story is the newest.
    # TODO: Find more efficient and elegant way of compare stories
    return (story_a["created_at"] > story_b["created_at"])

def build_tweet_string (story: dict) -> str:
    """
    Builds a string to be tweeted.

    :param story: Story to build tweet on.
    :return: String to be tweeted
    """
    # Transforms story's tags in hashtags
    hashtag_list = list(map(lambda tag: f"#{tag}", story["tags"]))
    # Joins hashtags as list
    hashtags = " ".join(hashtag_list)
    # Builds the base string
    base_string = TWEET_FORMAT.format(
        title=story["title"],
        author=story["author"],
        created_at=story["created_at"],
        short_id_url=story["short_id_url"],
        hashtags=hashtags
    )
    # Returns string
    return base_string

def get_latest_posted_tweet (bot: API) -> dict:
    """
    Gets the latest tweet posted and parses it.

    :param bot: Twitter bot to fetch the tweet from
    :return: Dictionary with "title", "short_id_url", "author" and "created_at" fields
    """
    # Gets its own Twitter ID
    twitter_id = bot.me().id
    # Gets its own last tweet
    latest_tweet = bot.user_timeline(id=twitter_id, tweet_mode="extended", count=1)[0]
    # Parses tweet to retrieve required fields
    result = parse(TWEET_FORMAT, latest_tweet.full_text)
    # Returns dictionary with the required fields, or None if the parsing has failed
    return result.named if result else None
    
def main ():
    # Creates bot
    bot = API(auth)
    print("Checking for new posts...")
    # Fetches JSON for newest story
    fetched_story = get_newest_story()
    # Fetches Twitter for the last published story
    last_posted_tweet = get_latest_posted_tweet(bot)
    # If the latest story is newest than the last posted, tweets it
    if (is_newest(fetched_story, last_posted_tweet)):
        # Builds tweet string
        tweet = build_tweet_string(fetched_story)
        # Posts tweet
        bot.update_status(tweet)
        print("Posted tweet: {tweet}".format(tweet=tweet))
    # Else prints a sleepy message
    else: print("Nothing new here, the bot goes back to sleep.")

if __name__ == "__main__":
    schedule.every(FETCH_INTERVAL).minutes.do(main)
    while (True):
        schedule.run_pending()