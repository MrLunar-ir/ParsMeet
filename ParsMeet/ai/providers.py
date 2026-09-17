import httpx
from typing import Optional, List, Dict

class BaseProvider:
    name = "base"
    requires_key = False

    def __init__(self, api_key=None, model=None):
        self.api_key = api_key
        self.model = model or self.default_model()
        self._client = None

    def default_model(self):
        return ""

    async def _get_client(self):
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=60)
        return self._client

    async def chat(self, messages, **kwargs):
        raise NotImplementedError

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

class OpenAIProvider(BaseProvider):
    name = "openai"
    requires_key = True

    def default_model(self):
        return "gpt-3.5-turbo"

    async def chat(self, messages, **kwargs):
        if not self.api_key:
            return "Error: OpenAI requires an API key."
        client = await self._get_client()
        try:
            r = await client.post("https://api.openai.com/v1/chat/completions", headers={"Authorization": f"Bearer {self.api_key}"}, json={"model": self.model, "messages": messages, "max_tokens": kwargs.get("max_tokens", 1000)}, timeout=60)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"].strip()
            return f"OpenAI Error: {r.status_code}"
        except Exception as e:
            return f"OpenAI Failed: {e}"

class GeminiProvider(BaseProvider):
    name = "gemini"
    requires_key = True

    def default_model(self):
        return "gemini-pro"

    async def chat(self, messages, **kwargs):
        if not self.api_key:
            return "Error: Gemini requires an API key."
        client = await self._get_client()
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
            contents = []
            for m in messages:
                role = "user" if m["role"] in ("user", "system") else "model"
                contents.append({"role": role, "parts": [{"text": m["content"]}]})
            r = await client.post(url, json={"contents": contents}, timeout=60)
            if r.status_code == 200:
                return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            return f"Gemini Error: {r.status_code}"
        except Exception as e:
            return f"Gemini Failed: {e}"

class OpenRouterProvider(BaseProvider):
    name = "openrouter"
    requires_key = True

    def default_model(self):
        return "openrouter/auto"

    async def chat(self, messages, **kwargs):
        if not self.api_key:
            return "Error: OpenRouter requires an API key."
        client = await self._get_client()
        try:
            r = await client.post("https://openrouter.ai/api/v1/chat/completions", headers={"Authorization": f"Bearer {self.api_key}"}, json={"model": self.model, "messages": messages, "max_tokens": kwargs.get("max_tokens", 1000)}, timeout=60)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"].strip()
            return f"OpenRouter Error: {r.status_code}"
        except Exception as e:
            return f"OpenRouter Failed: {e}"

class KeylessAIProvider(BaseProvider):
    name = "keylessai"
    requires_key = False

    def default_model(self):
        return "gpt-4o"

    async def chat(self, messages, **kwargs):
        client = await self._get_client()
        try:
            r = await client.post("https://keylessai.thryx.workers.dev/v1/chat/completions", headers={"Content-Type": "application/json"}, json={"model": self.model, "messages": messages, "max_tokens": kwargs.get("max_tokens", 1000)}, timeout=60)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"].strip()
            return f"KeylessAI Error: {r.status_code}"
        except Exception as e:
            return f"KeylessAI Failed: {e}"

class PollinationsProvider(BaseProvider):
    name = "pollinations"
    requires_key = False

    def default_model(self):
        return "pollinations"

    async def chat(self, messages, **kwargs):
        client = await self._get_client()
        try:
            prompt = messages[-1]["content"] if messages else ""
            system = ""
            for m in messages:
                if m["role"] == "system":
                    system = m["content"]
                    break
            url = f"https://api.pollinations.ai/prompt/{prompt}"
            if system:
                url += f"?system={system}"
            r = await client.get(url, timeout=30)
            if r.status_code == 200:
                return r.text.strip()
            return f"Pollinations Error: {r.status_code}"
        except Exception as e:
            return f"Pollinations Failed: {e}"

class AirforceProvider(BaseProvider):
    name = "airforce"
    requires_key = False

    def default_model(self):
        return "gpt-3.5-turbo"

    async def chat(self, messages, **kwargs):
        client = await self._get_client()
        try:
            r = await client.post("https://api.airforce/chat/completions", headers={"Content-Type": "application/json"}, json={"model": self.model, "messages": messages, "max_tokens": kwargs.get("max_tokens", 1000)}, timeout=60)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"].strip()
            return f"Airforce Error: {r.status_code}"
        except Exception as e:
            return f"Airforce Failed: {e}"

PROVIDERS = {
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
    "openrouter": OpenRouterProvider,
    "keylessai": KeylessAIProvider,
    "pollinations": PollinationsProvider,
    "airforce": AirforceProvider
}

def get_provider(name, api_key=None, model=None):
    if name not in PROVIDERS:
        raise ValueError(f"Unknown provider: {name}")
    return PROVIDERS[name](api_key=api_key, model=model)