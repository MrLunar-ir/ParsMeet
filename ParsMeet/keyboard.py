class Button:
    def __init__(self, text, callback_data=None, url=None):
        self.text = text
        self.callback_data = callback_data
        self.url = url

    def to_dict(self):
        if self.url:
            return {"text": self.text, "url": self.url}
        return {"text": self.text, "callback_data": self.callback_data}

class InlineKeyboard:
    def __init__(self):
        self.rows = []

    def row(self, *buttons):
        self.rows.append(list(buttons))
        return self

    def add(self, button):
        if not self.rows:
            self.rows.append([])
        self.rows[-1].append(button)
        return self

    def to_dict(self):
        return {"inline_keyboard": [[btn.to_dict() for btn in row] for row in self.rows]}

class ReplyKeyboard:
    def __init__(self, resize=True):
        self.rows = []
        self.resize = resize

    def row(self, *texts):
        self.rows.append(list(texts))
        return self

    def to_dict(self):
        return {"keyboard": self.rows, "resize_keyboard": self.resize}