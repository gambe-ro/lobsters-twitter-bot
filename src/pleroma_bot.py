from story import Story, StoryFormatter, get_new_stories
from storage import Storage
import logging
from mastodon import Mastodon
from requests import get
from config import *
import schedule

#  enables and get logger
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
SECRET_STORAGE="/storage/pleroma.secret"

PLEROMA_PATTERN = """**{title}** - {author}  
{tags}

[link]({story_url}) | [discussione]({discussion_url})
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
    pleroma = login()
    schedule.every(FETCH_INTERVAL).minutes.do(main)
    response = get(JSON_URL)
    json = response.json()

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
            pleroma.status_post(status=text,content_type="text/markdown")

        storage.save(new_stories[-1])
if __name__ == '__main__':
    main()
    schedule.every(FETCH_INTERVAL).minutes.do(main)
    while (True):
        schedule.run_pending()