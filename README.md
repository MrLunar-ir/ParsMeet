ParsMeet Library Help

Install the library:
```python
pip install ParsMeet
```

Create a bot:

```python
import ParsMeet
bot = ParsMeet.Bot(token="Your bot token")
```

Send a message:

```python
bot.send_message(chat_id, "message text")
```

Send a message with a glass button:

```python
bot.send_message(chat_id, "text", reply_markup={
"inline_keyboard": [
[{"text": "Button 1", "callback_data": "btn1"}],
[{"text": "Button 2", "callback_data": "btn2"}]
]
})
```

Send a photo:

```python
bot.send_photo(chat_id, "photo address or link", caption="Photo description or post text")
```

Send a file  :

```python
bot.send_document(chat_id, "file_address", caption="file_description")
```

Edit message :

```python
bot.edit_message(chat_id, message_id, "new text")
```

Delete message :

```python
bot.delete_message(chat_id, message_id)
```

Get messages:

```python
@bot.on_message_group()
def handler(data):
chat_id = data["chat_id"]
text = data["text"]
username = data["username"]
```

Get button clicks :

```python
@bot.on_callback_query()
def handler(data):
chat_id = data["chat_id"]
callback_data = data["data"]
```

Run bot :

```python
bot.run()
```

Shut down bot (from console)  :

```python
bot.off()
```

Full example (simple bot) :

```python
import ParsMeet

bot = ParsMeet.Bot(token="Your bot token")

@bot.on_message_group()
def handler(data):
chat_id = data["chat_id"]
text = data["text"]

if text == "/start":
bot.send_message(chat_id, "Hello, welcome")
elif text == "/help":
bot.send_message(chat_id, "Commands: /start and /help")

bot.run()
```