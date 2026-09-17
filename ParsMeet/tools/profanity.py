import re

class ProfanityFilter:
    def __init__(self, bad_words=None):
        self.bad_words = bad_words or []
        self.pattern = self._compile()

    def _compile(self):
        if not self.bad_words:
            return None
        return re.compile("|".join(map(re.escape, self.bad_words)), re.IGNORECASE)

    def check(self, text):
        if not self.pattern:
            return False
        return bool(self.pattern.search(text))

    def set_words(self, new_words):
        self.bad_words = new_words
        self.pattern = self._compile()