from datetime import date, datetime

from parse import parse

class Story(object):
    """
    Represents a Story as needed for posting on social networks.

    :param title: Title of the story.
    :param story_url: URL of the original post.  
    :param discussion_url: URL of the resource in the website (not original post's link).  
    :param author: Username of the post's author.  
    :param created_at: String with creation time of the story.  
    :param tags: List of story tags.    
    """

    MIN_TAGS_NUM = 3
    MIN_WORDS_NUM = 3

    def __init__(self, title: str, author: str, created_at: date, tags: [str], story_url: str = None, discussion_url: str = None):
        """
        Constructor of the object.

        :param title: Title of the story.
        :param story_url: URL of the original post.  
        :param discussion_url: URL of the resource in the website (not original post's link).  
        :param author: Username of the post's author.  
        :param created_at: String with creation time of the story.  
        :param tags: List of story tags.    
        """
        self.title = title
        self.story_url = story_url
        self.discussion_url = discussion_url
        self.author = author
        self.created_at = created_at
        self.tags = tags

    @classmethod
    def from_string(cls, pattern: str, string: str, created_at: date):
        """
        Deserializes the string to create a Story object.

        :param string: String with serialized fields as specified in pattern.
        :param created_at: Creation's timestamp, not provided in the pattern string.
        :return: Story with the deserialized fields. If the string doesn't respects pattern, returns None.
        """
        # Parses string
        result = parse(pattern, string)
        # If the pattern is not recognized returns None
        if result is None:
            raise ValueError("Invalid story pattern, cannot create a Story")
        # Creates object
        story = Story(
            title=result["title"],
            discussion_url=result["url"],
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
            discussion_url=story_data["short_id_url"],
            story_url=story_data["url"],
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
        return self.created_at > story.created_at

class StoryFormatter():

    def __init__(self, story: Story, pattern: str, max_length: int, min_tags_number: int = 1, min_words_number: int = 3, story_preview_length_func = None):

        self.pattern = pattern

        self.story = self.story
        
        self.min_tags_number = min_tags_number
        self.min_words_number = min_words_number
        self.max_length = max_length
        self.story_preview_length_func = story_preview_length_func or len

    def format_string(self) -> str:
        """
        Formats string to be posted.
        """

        current_tags = self.story.tags
        current_title_words = self.story.title_words.split(" ")
        
        while True:
            if self._estimate_story_length(current_tags, current_title_words) <= self.max_length:
                return self._fill_template(tags=current_tags, title_words=current_title_words)

            if len(current_tags) > self.min_tags_number:
                current_tags = current_tags[:-1]
                continue

            if len(current_title_words) > self.min_words_number:
                current_title_words = current_title_words[:-1]
                continue

            raise ValueError("No Valid Tweet could be produced.")

    def _estimate_story_length(self, tags, title_words):
        string = self._fill_template(tags, title_words)
        return self.story_preview_length_func(string)

    def _fill_template(self, tags=None, title_words=None):

        hashtag_list = list(
            map(lambda tag: f"#{tag}" if tag[0] != '#' else tag, tags or self.story.tags))

        # Joins hashtags as list
        hashtags = " ".join(hashtag_list)

        # Builds the base string
        return self.pattern.format(
            title=" ".join(title_words) if title_words else self.story.title,
            author=self.story.author,
            url=self.story.discussion_url,
            tags=hashtags
        )

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
