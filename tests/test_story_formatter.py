import pytest

from story import StoryFormatter, Story
from twitter_bot import TwitterStoryFormatter
from telegram_bot import TelegramStoryFormatter
@pytest.mark.parametrize("author", ["some_author"])
@pytest.mark.parametrize("tags, title, expected_length", [
    [["tag_1", "tag_2"], "word ", 78],
    [["tag_1", "tag_2", "tag3", "tag4"], "word " * int(280 / 5), 270],
    [["tag_1", "tag_2", "tag3"], "word " * 50, 270]
])
def test_valid(tags, title, author, expected_length):
    formatter = TwitterStoryFormatter()
    s = Story(title=title, story_url="https://someurl.com", discussion_url="https://someurl2.com",
              author=author, created_at=None, tags=tags)
    string = str(formatter.format_string(s))
    assert len(string) == expected_length

def test_failing ():
    formatter = TwitterStoryFormatter()

    s = Story(title="failing_title"*50, story_url="https://someurl.com", discussion_url="https://someurl2.com",
          author="author", created_at=None, tags=[])
    with pytest.raises(ValueError):
      formatter.format_string(s)


@pytest.mark.parametrize("author", ["some_author"])
@pytest.mark.parametrize("tags, title, expected_length", [
    [["tag_1", "tag_2"], "word ", 107],
    [["tag_1", "tag_2", "tag3", "tag4"], "word " * int(280 / 5), 394],
    [["tag_1", "tag_2", "tag3"], "word " * 50, 358]
])
def test_valid_telegram(tags, title, author, expected_length):
    formatter = TelegramStoryFormatter()
    s = Story(title=title, story_url="https://someurl.com", discussion_url="https://someurl2.com",
              author=author, created_at=None, tags=tags)
    string = str(formatter.format_string(s))
    assert len(string) == expected_length

def test_failing ():
    formatter = TelegramStoryFormatter()

    s = Story(title="failing_title"*500, story_url="https://someurl.com", discussion_url="https://someurl2.com",
              author="author", created_at=None, tags=[])
    with pytest.raises(ValueError):
        formatter.format_string(s)