from parse import parse

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

    PATTERN = "{title} - {url} ({author}, {created_at}) {tags}"

    def __init__ (self, title: str, url: str, author: str, created_at: str, tags: [str]):
        """
        Constructor of the object.

        :param title: Title of the story.
        :param url: URL of the resource in the website (not original post's link).
        :param author: Username of the post's author.
        :param created_at: String with creation time of the story
        :param tags: List of story tags
        """
        self.title = title
        self.url = url
        self.author = author
        self.created_at = created_at
        self.tags = tags

    @classmethod
    def from_string (self, string: str):
        """
        Deserializes the string to create a Story object.
        
        :param string: String with serialized fields as specified in PATTERN.
        :return: Story with the deserialized fields. If the string doesn't respects pattern, returns None.
        """
        # Parses string
        result = parse(self.PATTERN, string)
        # If the pattern is not recognized returns None
        if (result is None): return None
        # Creates object
        story = Story(
            title=result["title"],
            url=result["url"],
            author=result["author"],
            created_at=result["created_at"],
            tags=result["tags"]
        )
        # Returns story
        return story
    
    @classmethod
    def from_json_dict (self, json: dict):
        """
        Uses fields of the JSON got from the webstie to build story.
        
        :param json: Dictionary representing the JSON got from the Lobste.rs website.
        :return: Story created from the dictionary fields.
        """
        story = Story(
            title=json["title"],
            url=json["short_id_url"],
            author=json["submitter_user"]["username"],
            created_at=json["created_at"],
            tags=json["tags"]
        )
        return story
        
    def is_newer_of (self, story) -> bool:
        """
        :param story: Story to be compared.
        :return: True if self is newer of the other story, False otherwise.
        """
        # TODO: Find more efficient and elegant way to compare stories
        return (self.created_at > story.created_at)

    def __str__ (self) -> str:
        """
        Builds a string to be tweeted.

        :param story: Story to build tweet on.  
        :return: String to be tweeted
        """
        # Transforms story's tags in hashtags (only if they are not transformed already)
        hashtag_list = list(map(lambda tag: f"#{tag}" if tag[0] != '#' else tag, self.tags))
        # Joins hashtags as list
        hashtags = " ".join(hashtag_list)
        # Builds the base string
        base_string = self.PATTERN.format(
            title=self.title,
            author=self.author,
            created_at=self.created_at,
            url=self.url,
            tags=hashtags
        )
        # Returns string
        return base_string

def get_new_stories (latest_story: Story, json: dict) -> [Story]:
    """
    Gets the stories in the JSON dictionary published after story.

    :param latest_story: Latest story published as a tweet.
    :param json: Dictionary with data from the Lobste.rs website.  
    :return: List of stories published after story (maybe empty), or the latest published intem in JSON if story doesn't exists.
    """
    # List of stories published
    stories = []
    # If latest story doesn't exists (this is the first tweet) gets only the latest story
    if (latest_story is None):
        story = Story.from_json_dict(json[0])
        stories.append(story)
    # Else gets the latest stories published
    else:
        for story_json in json:
            # Creates story from json
            story = Story.from_json_dict(story_json)
            # Compares current story and last published story
            if (story.is_newer_of(latest_story)): stories.append(story)
            else: break
    # Reverts list (from older to newer) and returns it
    stories.reverse()
    return stories