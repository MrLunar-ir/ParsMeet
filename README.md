Quick Start

```python
import ParsMeet
from ParsMeet import Filters

bot = ParsMeet.Bot(token="YOUR_TOKEN", ai_provider="keylessai")

@bot.on_message(Filters.command & Filters.command_is("start"))
def start_handler(data):
    bot.send_message(data["chat_id"], "Hello!")

@bot.on_askai()
def ai_handler(chat_id, text, username):
    return text

bot.run()
```

CLI

```bash
parsmeet new mybot
cd mybot
python bot.py
```

Features

· AI (OpenAI, Gemini, OpenRouter, KeylessAI, Pollinations, Airforce)
· FSM conversations
· Scheduler (every/at/once)
· i18n multi-language
· Webhook & Long Polling
· Plugin system
· Broadcast queue
· Rate limit, cooldown, cache
· Inline & Reply keyboards (OOP)
· Middleware
· AntiLink, AntiSpam, Profanity, Captcha, ForceJoin, WarnSystem
· Dashboard
· Full type hints and tests

License
MIT
