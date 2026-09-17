import re

class AntiLink:
    def __init__(self, extra_patterns=None):
        base = r'(https?://|www\.|@\w+|bit\.ly|tinyurl\.com|t\.co|codemeet\.chat)'
        if extra_patterns:
            base += "|" + "|".join(re.escape(p) for p in extra_patterns)
        self.pattern = re.compile(base, re.IGNORECASE)

    def check(self, text):
        return bool(self.pattern.search(text))