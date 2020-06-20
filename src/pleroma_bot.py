from story import Story, StoryFormatter, get_new_stories
from storage import Storage
import logging
import time
from mastodon import Mastodon
from requests import get
from config import *
import schedule
from mastodon import MastodonError
from logging.config import fileConfig
import os.path
from os import environ
import sentry_sdk

if 'SENTRY_URL' in environ:
    sentry_sdk.init(environ["SENTRY_URL"])

#  enables and get logger
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
SECRET_STORAGE="/storage/pleroma.secret"

PLEROMA_PATTERN = """{title} - {author}  
{tags}

Link: {story_url}
Discussione: {discussion_url}
"""
class PleromaStoryFormatter(StoryFormatter):
    def __init__(self):

        super(PleromaStoryFormatter, self).__init__(

            pattern=PLEROMA_PATTERN,
            max_length=512
        )


class PleromaStorage(Storage):
    file_path = "/storage/pleroma_bot_storage"


def login():
    Mastodon.create_app("test", api_base_url=BASE_URL, to_file =SECRET_STORAGE)

    pleroma = Mastodon(
        client_id = SECRET_STORAGE,
        api_base_url=BASE_URL
    )
    pleroma.log_in(USERNAME, PASSWORD, to_file =SECRET_STORAGE)
    return pleroma

def main():
    try:
        pleroma = login()
    except MastodonError:
        logger.error("login failed", exc_info=True)
        return
    except KeyError:
        logger.error("login failed", exc_info=True)
        return

    logger.debug("Logged in")
    try:
        response = get(JSON_URL)
        json = response.json()
    except Exception as e:
        logger.error("Failed to connect to gambe.ro. Skipping.")
        return
    
    logger.debug("Downloaded stories")
    storage = PleromaStorage()
    latest= storage.load()
    if latest:
        new_stories = get_new_stories(latest, json)
    else:
        new_stories = [Story.from_json_dict(json[0])]

    if len(new_stories) == 0:
        logger.info("No new stories found since last check")
    else:
        for story in new_stories:
            text = PleromaStoryFormatter().format_string(story)
            pleroma.status_post(status=text,content_type="text/html")

        storage.save(new_stories[-1])
if __name__ == '__main__':
    if os.path.isfile(LOGGING_CONF_FILE):
        fileConfig(LOGGING_CONF_FILE)
    main()
    schedule.every(FETCH_INTERVAL).minutes.do(main)

    while (True):
        schedule.run_pending()
        time.sleep(1000)
