from .providers import get_provider
from .memory import ConversationMemory

class AIManager:
    def __init__(self, provider="keylessai", api_key=None, model=None, memory_enabled=True):
        self.provider_name = provider
        self.api_key = api_key
        self.model = model
        self.provider = get_provider(provider, api_key, model)
        self.memory_enabled = memory_enabled
        self.memory = ConversationMemory()
        self._fallback_order = ["keylessai", "airforce", "pollinations"]

    def set_provider(self, name, api_key=None, model=None):
        self.provider_name = name
        self.api_key = api_key
        self.model = model
        self.provider = get_provider(name, api_key, model)

    def set_system_prompt(self, user_id, prompt):
        self.memory.set_system(user_id, prompt)

    async def chat(self, user_id, prompt, system_prompt=""):
        messages = []
        sys_prompt = system_prompt or self.memory.get_system(user_id)
        if sys_prompt:
            messages.append({"role": "system", "content": sys_prompt})
        if self.memory_enabled:
            messages.extend(self.memory.get(user_id))
        messages.append({"role": "user", "content": prompt})
        answer = await self.provider.chat(messages)
        if answer.startswith(("OpenAI Error", "OpenAI Failed", "Gemini Error", "Gemini Failed", "OpenRouter Error", "OpenRouter Failed", "KeylessAI Error", "KeylessAI Failed", "Airforce Error", "Airforce Failed", "Pollinations Error", "Pollinations Failed")):
            answer = await self._try_fallbacks(messages)
        if self.memory_enabled and answer and not answer.startswith(("Error", "Failed")):
            self.memory.add(user_id, "user", prompt)
            self.memory.add(user_id, "assistant", answer)
        return answer

    async def _try_fallbacks(self, messages):
        for name in self._fallback_order:
            if name == self.provider_name:
                continue
            try:
                provider = get_provider(name)
                answer = await provider.chat(messages)
                if answer and not answer.startswith(("Error", "Failed")):
                    return answer
            except Exception:
                continue
        return "AI services are currently unavailable."

    def clear_memory(self, user_id):
        self.memory.clear(user_id)

    def clear_all_memory(self):
        self.memory.clear_all()

    async def close(self):
        await self.provider.close()