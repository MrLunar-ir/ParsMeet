class Filter:
    def __init__(self, func):
        self.func = func

    def __call__(self, data):
        return self.func(data)

    def __and__(self, other):
        return Filter(lambda d: self(d) and other(d))

    def __or__(self, other):
        return Filter(lambda d: self(d) or other(d))

    def __invert__(self):
        return Filter(lambda d: not self(d))

class Filters:
    text = Filter(lambda d: d.get("text") is not None and not d.get("text", "").startswith("/"))
    command = Filter(lambda d: d.get("text", "").startswith("/"))
    private = Filter(lambda d: d.get("chat_type") == "private")
    group = Filter(lambda d: d.get("chat_type") in ("group", "supergroup"))
    admin = Filter(lambda d: d.get("is_admin", False))
    reply = Filter(lambda d: d.get("reply_to_message") is not None)
    photo = Filter(lambda d: d.get("photo") is not None)
    document = Filter(lambda d: d.get("document") is not None)

    @staticmethod
    def contains(word):
        return Filter(lambda d: word.lower() in d.get("text", "").lower())

    @staticmethod
    def command_is(name):
        return Filter(lambda d: d.get("text", "").split()[0] == f"/{name}")

    @staticmethod
    def custom(func):
        return Filter(func)