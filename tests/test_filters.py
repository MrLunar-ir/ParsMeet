from ParsMeet.filters import Filters

def test_text_filter():
    assert Filters.text({"text": "hello"}) is True
    assert Filters.text({"text": "/start"}) is False

def test_command_filter():
    assert Filters.command({"text": "/start"}) is True
    assert Filters.command({"text": "hello"}) is False

def test_and_operator():
    combined = Filters.text & Filters.group
    assert combined({"text": "hi", "chat_type": "group"}) is True
    assert combined({"text": "hi", "chat_type": "private"}) is False

def test_or_operator():
    combined = Filters.private | Filters.group
    assert combined({"chat_type": "private"}) is True
    assert combined({"chat_type": "group"}) is True

def test_invert_operator():
    inverted = ~Filters.text
    assert inverted({"text": "/cmd"}) is True