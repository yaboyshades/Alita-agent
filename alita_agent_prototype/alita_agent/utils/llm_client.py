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
            openai.api_key = self.config.openai_api_key
            response = await openai.ChatCompletion.acreate(
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
        elif self.provider == "deepseek":
            # Placeholder for DeepSeek API call
            # You would use requests or httpx to call DeepSeek's API
            raise NotImplementedError("DeepSeek integration not implemented yet.")
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")
