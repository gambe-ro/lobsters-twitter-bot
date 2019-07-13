from os import getenv
from time import sleep
from datetime import datetime

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

def get_last_posted_tweet (bot: API) -> dict:
    """
    Gets the last tweet posted and parses it.

    :param bot: Twitter bot to fetch the tweet from.  
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

def is_newest (story_a: dict, story_b: dict) -> bool:
    """
    Returns True if the first story is newest than the second one.

    :param story_a: Story to be verified as newest.  
    :param story_b: Other story to be compared.  
    :return: True if story_a is newest than story_b, False otherwise.
    """
    # If created_at fields are different, first story is the newest.
    # TODO: Find more efficient and elegant way of compare stories
    return (story_a["created_at"] > story_b["created_at"])

def get_new_stories (latest_story: dict) -> [dict]:
    """
    Gets the stories posted on the site after story.

    :param latest_story: Latest story published as a tweet.  
    :return: List of stories published after story, or the latest published intem on site if story doesn't exists.
    """
    # Gets the webpage
    request = get(JSON_URL)
    # Extrapolates JSON content
    json_result = request.json()
    # List of stories published after story
    stories = []
    # If latest story doesn't exists (this is the first tweet) gets only the latest story
    if (latest_story is None): stories.append(json_result[0])
    # Else gets the latest stories published
    else:
        for story in json_result:
            if (not is_newest(story, latest_story)): break
            stories.append(story)
    # Reverts list (from older to newer) and returns it
    stories.reverse()
    return stories

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
        author=story["submitter_user"]["username"],
        created_at=story["created_at"],
        short_id_url=story["short_id_url"],
        hashtags=hashtags
    )
    # Returns string
    return base_string
    
def main ():
    # Creates bot
    bot = API(auth)
    print("Checking for new posts...")
    # Fetches Twitter for the last published stories
    last_posted_tweet = get_last_posted_tweet(bot)
    # Fetches JSON for new stories
    new_stories = get_new_stories(last_posted_tweet)
    # Tweets all the new stories
    print("[{time}]".format(time=datetime.now()), end=" ")
    if (len(new_stories) == 0): print("Nothing new here, the bot is back to sleep.")
    else:
        for story in new_stories:
            tweet = build_tweet_string(story)
            bot.update_status(tweet)
            print("Tweeted: {tweet}".format(tweet=tweet))

if __name__ == "__main__":
    schedule.every(FETCH_INTERVAL).minutes.do(main)
    while (True):
        schedule.run_pending()