import pytest

from twitter_bot import Story, DefaultTwitterPublishConfig


@pytest.mark.parametrize("author", ["some_author"])
@pytest.mark.parametrize("tags, title, expected_length", [
    [["tag_1", "tag_2"], "word ", 55],
    [["tag_1", "tag_2", "tag3", "tag4"], "word " * int(280 / 5), 275],
    [["tag_1", "tag_2", "tag3"], "word " * 50, 275]
])
def test_valid(tags, title, author, expected_length):
    s = Story(title, "https://someurl.com", author, created_at=None, tags=tags,
              publish_config=DefaultTwitterPublishConfig())
    assert len(str(s)) == expected_length

def test_failing ():
    author = "failing_author" * 50
    s = Story("test", "https://someurl.com", author, created_at=None, tags=["tag_1", "tag_2"],
              publish_config=DefaultTwitterPublishConfig())

    with pytest.raises(ValueError):
        str(s)