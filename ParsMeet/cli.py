import os
import argparse

TEMPLATE_BOT = """import ParsMeet
from ParsMeet import Filters

bot = ParsMeet.Bot(token="{token}", ai_provider="{ai_provider}", ai_memory=True)

@bot.on_message(Filters.command & Filters.command_is("start"))
def start_handler(data):
    bot.send_message(data["chat_id"], "Hello! I am alive.")

@bot.on_askai()
def ai_handler(chat_id, text, username):
    return text

if __name__ == "__main__":
    bot.run()
"""

TEMPLATE_ENV = """PARSMEET_TOKEN=your_bot_token_here
PARSMEET_AI_PROVIDER=keylessai
PARSMEET_AI_KEY=
"""

TEMPLATE_README = """# My ParsMeet Bot

Generated with parsmeet new.

## Run

pip install ParsMeet
python bot.py
"""

def new_project(name):
    if os.path.exists(name):
        print(f"Error: Folder '{name}' already exists.")
        return False
    os.makedirs(name)
    os.makedirs(os.path.join(name, "plugins"), exist_ok=True)
    os.makedirs(os.path.join(name, "data"), exist_ok=True)
    with open(os.path.join(name, "bot.py"), "w", encoding="utf-8") as f:
        f.write(TEMPLATE_BOT.format(token="YOUR_TOKEN_HERE", ai_provider="keylessai"))
    with open(os.path.join(name, ".env"), "w", encoding="utf-8") as f:
        f.write(TEMPLATE_ENV)
    with open(os.path.join(name, "README.md"), "w", encoding="utf-8") as f:
        f.write(TEMPLATE_README)
    with open(os.path.join(name, "plugins", "__init__.py"), "w", encoding="utf-8") as f:
        f.write("")
    print(f"Project '{name}' created successfully.")
    return True

def main():
    parser = argparse.ArgumentParser(prog="parsmeet", description="ParsMeet CLI")
    sub = parser.add_subparsers(dest="command")
    new_cmd = sub.add_parser("new", help="Create a new ParsMeet bot project")
    new_cmd.add_argument("name", help="Project folder name")
    sub.add_parser("version", help="Show ParsMeet version")
    args = parser.parse_args()
    if args.command == "new":
        new_project(args.name)
    elif args.command == "version":
        from . import __version__
        print(f"ParsMeet {__version__}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()