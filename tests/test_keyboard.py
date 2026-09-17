from ParsMeet.keyboard import Button, InlineKeyboard, ReplyKeyboard

def test_button():
    b = Button("Click", callback_data="click")
    assert b.to_dict() == {"text": "Click", "callback_data": "click"}

def test_button_url():
    b = Button("Site", url="https://example.com")
    assert b.to_dict() == {"text": "Site", "url": "https://example.com"}

def test_inline_keyboard():
    kb = InlineKeyboard().row(Button("A", "a"), Button("B", "b"))
    result = kb.to_dict()
    assert len(result["inline_keyboard"]) == 1
    assert len(result["inline_keyboard"][0]) == 2

def test_reply_keyboard():
    kb = ReplyKeyboard().row("Yes", "No")
    result = kb.to_dict()
    assert result["keyboard"] == [["Yes", "No"]]
    assert result["resize_keyboard"] is True