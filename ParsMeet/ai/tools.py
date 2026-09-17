class AITools:
    def __init__(self, manager):
        self.manager = manager

    async def summarize(self, chat_id, messages):
        text = "\n".join([f"{m.get('username', 'Unknown')}: {m.get('text', '')}" for m in messages])
        prompt = f"Summarize the following group chat in 3-5 sentences:\n\n{text}"
        return await self.manager.chat(chat_id, prompt, system_prompt="You are a helpful summarizer.")

    async def translate(self, chat_id, text, target_lang):
        prompt = f"Translate the following text to {target_lang}. Return only the translation:\n\n{text}"
        return await self.manager.chat(chat_id, prompt, system_prompt="You are a translator.")

    async def detect_spam(self, chat_id, text):
        prompt = f"Is the following message spam, advertisement, or scam? Answer only YES or NO:\n\n{text}"
        answer = await self.manager.chat(chat_id, prompt, system_prompt="Answer only YES or NO.")
        return answer.strip().upper().startswith("YES")

    async def classify(self, chat_id, text, categories):
        cats = ", ".join(categories)
        prompt = f"Classify the following message into one of these categories: {cats}. Answer only with the category name:\n\n{text}"
        return await self.manager.chat(chat_id, prompt, system_prompt="You are a classifier.")