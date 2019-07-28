from parse import parse
from datetime import date, datetime

class Story (object):
    """
    Represents a Story as needed for posting on social networks.

    :param title: Title of the story.  
    :param url: URL of the resource in the website (not original post's link).  
    :param author: Username of the post's author.  
    :param created_at: String with creation time of the story.  
    :param tags: List of story tags.  
    :param PATTERN: String representing the pattern to deserialize and serialize a story.  
    """

    PATTERN = "{title} - {url} ({author}) {tags}"

    def __init__(self, title: str, url: str, author: str, created_at: date, tags: [str]):
        """
        Constructor of the object.

        :param title: Title of the story.
        :param url: URL of the resource in the website (not original post's link).
        :param author: Username of the post's author.
        :param created_at: Creation time and date of the story
        :param tags: List of story tags
        """
        self.title = title
        self.url = url
        self.author = author
        self.created_at = created_at
        self.tags = tags

    @classmethod
    def from_string(cls, string: str, created_at: date):
        """
        Deserializes the string to create a Story object.

        :param string: String with serialized fields as specified in PATTERN.
        :param created_at: Creation's timestamp, not provided in the PATTERN string.
        :return: Story with the deserialized fields. If the string doesn't respects pattern, returns None.
        """
        # Parses string
        result = parse(cls.PATTERN, string)
        # If the pattern is not recognized returns None
        if result is None:
            raise ValueError("Invalid story pattern, cannot create a Story")
        # Creates object
        story = Story(
            title=result["title"],
            url=result["url"],
            author=result["author"],
            created_at=created_at,
            tags=result["tags"]
        )
        # Returns story
        return story

    @classmethod
    def from_json_dict(cls, story_data: dict):
        """
        Uses fields of a dict to build story.

        :param story_data: Dictionary representing the JSON got from the Lobste.rs website.
        :return: Story created from the dictionary fields.
        """
        story = Story(
            title=story_data["title"],
            url=story_data["short_id_url"],
            author=story_data["submitter_user"]["username"],
            created_at=datetime.strptime(story_data["created_at"], "%Y-%m-%dT%H:%M:%S.%f%z"),
            tags=story_data["tags"]
        )
        return story

    def is_newer_of(self, story) -> bool:
        """
        :param story: Story to be compared.
        :return: True if self is newer of the other story, False otherwise.
        """
        # TODO: Find more efficient and elegant way to compare stories
        return (self.created_at > story.created_at)

    def __str__(self) -> str:
        """
        Builds a string to be tweeted.

        :param story: Story to build tweet on.  
        :return: String to be tweeted
        """
        # Transforms story's tags in hashtags (only if they are not transformed already)
        hashtag_list = list(
            map(lambda tag: f"#{tag}" if tag[0] != '#' else tag, self.tags))
        # Joins hashtags as list
        hashtags = " ".join(hashtag_list)
        # Builds the base string
        base_string = self.PATTERN.format(
            title=self.title,
            author=self.author,
            url=self.url,
            tags=hashtags
        )
        # Returns string
        return base_string


def get_new_stories(latest_story: Story, source_data: dict) -> [Story]:
    """
    Gets the stories in the JSON dictionary published after story.

    :param latest_story: Latest story published as a tweet.
    :param source_data: Dictionary with data from the Lobste.rs website.
    :return: List of stories published after story (maybe empty), or the latest published item in JSON
     if story doesn't exists.
    """
    # List of stories published
    stories = []
    for story_json in source_data:
        # Creates story from json
        story = Story.from_json_dict(story_json)
        # Compares current story and last published story
        if story.is_newer_of(latest_story):
            stories.append(story)
        else:
            break
    # Reverses list (from older to newer) and returns it
    stories.reverse()
    return stories
