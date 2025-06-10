import os
from typing import Optional

class LLMClient:
    def __init__(self, config):
        self.provider = (getattr(config, 'llm_provider', None) or "openai").lower()
        self.model = getattr(config, 'llm_model', None) or "gpt-4"
        self.config = config

    async def generate(self, prompt: str) -> str:
        if self.provider == "openai":
            import openai
            client = openai.AsyncOpenAI(api_key=self.config.openai_api_key)
            response = await client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        elif self.provider == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=self.config.gemini_api_key)
            model = genai.GenerativeModel(self.model)
            response = await model.generate_content_async(prompt)
            return response.text.strip()
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")
