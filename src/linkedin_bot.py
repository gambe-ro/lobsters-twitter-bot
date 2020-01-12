from linkedin_v2.linkedin import LinkedInAuthentication, PERMISSIONS, LinkedInApplication
from story import Story, StoryFormatter, get_new_stories
from storage import Storage
import logging
from requests import get
from config import *
import schedule
from logging.config import fileConfig
import os.path


#  enables and get logger
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
SECRET_STORAGE="/storage/linkedin.secret"

LINKEDIN_PATTERN = """{author}  
{tags}
Discussione: {discussion_url}
"""

def login()->LinkedInApplication:
    if not LINKEDIN_TOKEN:
        auth = LinkedInAuthentication(LINKEDIN_KEY, LINKEDIN_SECRET, 'http://localhost:8000/',
                                      ["w_share"])
        print(auth.authorization_url)
        authorization_code = input("Please insert authorization_code")
        auth.authorization_code = authorization_code
        token = auth.get_access_token()
    else:
        token = LINKEDIN_TOKEN
    return LinkedInApplication(token=token)

def make_linkedin_request(story):
    return {
        "content": {
            "contentEntities": [
                {
                    "entityLocation": story.story_url,

                }
            ],
            "title": story.title
        },
        "distribution": {
            "linkedInDistributionTarget": {}
        },
        "text": {
            "text": LinkedinStoryFormatter().format_string(story)
        }
    }

class LinkedinStoryFormatter(StoryFormatter):
    def __init__(self):

        super(LinkedinStoryFormatter, self).__init__(

            pattern=LINKEDIN_PATTERN,
            max_length=512
        )
class LinkedinStorage(Storage):
    file_path = "/storage/linkedin_bot_storage"

def main():

    application = login()
    logger.debug("Logged in")
    try:
        response = get(JSON_URL)
        json = response.json()
    except Exception as e:
        logger.error("Failed to connect to gambe.ro. Skipping.")
        return

    logger.debug("Downloaded stories")
    storage = LinkedinStorage()
    latest= storage.load()
    if latest:
        new_stories = get_new_stories(latest, json)
    else:
        new_stories = [Story.from_json_dict(json[0])]

    if len(new_stories) == 0:
        logger.info("No new stories found since last check")
    else:
        for story in new_stories:
            response = application.make_request(method="POST",
                                     url="https://api.linkedin.com/v2/shares",
                                     data= make_linkedin_request(story)
                                     )
            logger.debug(response.status_code)
            logger.debug(response.content)
            print(response.content)
        storage.save(new_stories[-1])

if __name__ == '__main__':
    if os.path.isfile(LOGGING_CONF_FILE):
        fileConfig(LOGGING_CONF_FILE)
    main()
    schedule.every(FETCH_INTERVAL).minutes.do(main)

    while (True):
        schedule.run_pending()