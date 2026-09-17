class I18n:
    def __init__(self, default_locale="en"):
        self.default_locale = default_locale
        self.translations = {}
        self.user_locales = {}
        self._load_defaults()

    def _load_defaults(self):
        self.translations["en"] = {
            "welcome": "Welcome!",
            "goodbye": "Goodbye!",
            "error": "An error occurred.",
            "not_authorized": "You are not authorized.",
            "help": "Available commands:"
        }
        self.translations["fa"] = {
            "welcome": "خوش آمدید!",
            "goodbye": "خداحافظ!",
            "error": "خطایی رخ داد.",
            "not_authorized": "شما مجاز نیستید.",
            "help": "دستورات موجود:"
        }

    def add_locale(self, locale, translations):
        if locale not in self.translations:
            self.translations[locale] = {}
        self.translations[locale].update(translations)

    def set_locale(self, user_id, locale):
        self.user_locales[user_id] = locale

    def get_locale(self, user_id):
        return self.user_locales.get(user_id, self.default_locale)

    def text(self, key, user_id=None, **kwargs):
        locale = self.get_locale(user_id) if user_id else self.default_locale
        trans = self.translations.get(locale, {})
        if key not in trans:
            trans = self.translations.get(self.default_locale, {})
        template = trans.get(key, key)
        return template.format(**kwargs) if kwargs else template