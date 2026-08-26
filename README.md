ParsMeet Library Guide (Version 1.3.0)

Install the library:

```python
pip install ParsMeet
```

Create a bot:

```python
import ParsMeet
bot = ParsMeet.Bot(token="Your bot token", ai_key="AI key (optional)")
```

Send a message:

```python
bot.send_message(chat_id, "Message text")
```

Send a message with a glass button:

```python
btn1 = bot.create_callback("Button 1", "btn1")
btn2 = bot.create_callback("Button 2", "btn2")
bot.send_message(chat_id, "Text", reply_markup={"inline_keyboard": [[btn1], [btn2]]})
```

Send a photo:

```python
bot.send_photo(chat_id, "Photo address or link",  caption="Image description")
```

Send file:

```python
bot.send_document(chat_id, "file_address", caption="file_description")
```

Reply to message:

```python
bot.reply_message(chat_id, message_id, "reply text")
```

Edit message:

```python
bot.edit_message(chat_id, message_id, "new text")
```

Delete message:

```python
bot.delete_message(chat_id, message_id)
```

Receive messages:

```python
@bot.on_message_all()
def handler(data):
chat_id = data["chat_id"]
text = data["text"]
username = data["username"]
```

Receive button clicks:

```python
@bot.on_callback_query()
def handler(data):
 chat_id = data["chat_id"]
callback_data = data["data"]
```

Group management (optional):

```python
bot.ban_user(chat_id, user_id)
bot.unban_user(chat_id, user_id)
bot.promote_user(chat_id, user_id)
bot.demote_user(chat_id, user_id)
bot.pin_message(chat_id, message_id)
```

Connect to AI:

```python
response = bot.ask_ai("Your question")
bot.send_message(chat_id, response)
```

Send to all:

```python
bot.broadcast("Message text for everyone")
```

Run the bot:

```python
bot.run()
```

Shut down the bot (from the console):

```python
bot.off()
```

Full example (bot  simple):

```python
import ParsMeet

bot = ParsMeet.Bot(token="Your bot token")

@bot.on_message_all()
def handler(data):
chat_id = data["chat_id"]
text = data["text"]

if text == "/start":
btn = bot.create_callback("Menu", "menu")
bot.send_message(chat_id, "Hello, welcome", reply_markup={"inline_keyboard": [[btn]]})
elif text == "/help":
bot.send_message(chat_id, "Commands: /start and /help")

bot.run()
```