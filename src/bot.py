from os import getenv
from time import sleep

from tweepy import OAuthHandler, API
from requests import get

# Picks bot parameters from environment
CONSUMER_KEY = getenv("CONSUMER_KEY")
CONSUMER_SECRET = getenv("CONSUMER_SECRET")
ACCESS_TOKEN = getenv("ACCESS_TOKEN")
ACCESS_SECRET = getenv("ACCESS_SECRET")

JSON_URL = getenv("JSON_URL")

INTERVAL = int(getenv("FETCH_INTERVAL", default=15)) * 60

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
    json = request.json()
    # Gets first element
    return json[0]

def is_newest (story_a: dict, story_b: dict) -> bool:
    """
    Returns True if the first story is newest than the second one.

    :param story_a: Story to be verified as newest.
    :param story_b: Other story to be compared.
    :return: True if story_a is newest than story_b, False otherwise.
    """
    # If there is no second story, first is newest.
    if (story_b == None): return True
    # If titles are different, first story is newest.
    return (story_a["title"] != story_b["title"])

def get_tweet_string (story: dict) -> str:
    """
    Builds a string to be tweeted.

    :param story: Story to build tweet on.
    :return: String to be tweeted
    """
    # Base string
    base_string = "{title} - {url} ".format(title=story["title"], url=story["short_id_url"])
    # Appends tags as hashtags
    for tag in story["tags"]:
        base_string += "#{tag} ".format(tag=tag)
    # Returns string
    return base_string

if __name__ == "__main__":
    # Creates bot
    bot = API(auth)
    print("Bot successifully created, starting.")
    # When the bot starts, last posted story doesn't exists
    last_posted_story = None
    # Infinite loop of execution
    while (True):
        print("Checking for new posts...")
        # Fetches JSON for newest story
        fetched_story = get_newest_story()
        # If the latest story is newest than the last posted, tweets it
        if (is_newest(fetched_story, last_posted_story)):
            # Builds tweet string
            tweet = get_tweet_string(fetched_story)
            # Posts tweet
            bot.update_status(tweet)
            # Updates last posted story
            last_posted_story = fetched_story
            print("Posted tweet: {tweet}".format(tweet=tweet))
        # Else prints a sleepy message
        else:
            print("Nothing new, the bot goes back to sleep,")
        # Pauses for the given interval
        sleep(INTERVAL)