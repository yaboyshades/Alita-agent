class LLMClient:
    def __init__(self, config):
        self.provider = (getattr(config, "llm_provider", None) or "gemini").lower()
        self.model = getattr(config, "llm_model", None) or "gemini-pro"
        self.config = config

    async def generate(self, prompt: str) -> str:
        if self.provider == "openai":
            try:
                import openai
            except ModuleNotFoundError as exc:
                raise ValueError(
                    "openai package is required to use the OpenAI provider"
                ) from exc

            client = openai.AsyncOpenAI(api_key=self.config.openai_api_key)
            response = await client.chat.completions.create(
                model=self.model, messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        elif self.provider == "gemini":
            try:
                import google.generativeai as genai
            except ModuleNotFoundError as exc:
                raise ValueError(
                    "google-generativeai package is required to use the Gemini provider"
                ) from exc

            genai.configure(api_key=self.config.gemini_api_key)
            model = genai.GenerativeModel(self.model)
            response = await model.generate_content_async(prompt)
            return response.text.strip()
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")
