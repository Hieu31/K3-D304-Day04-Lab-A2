from providers.openai_provider import OpenAIProvider


class GroqProvider(OpenAIProvider):
    def __init__(self):
        super().__init__(
            api_key_env="GROQ_API_KEY",
            base_url="https://api.groq.com/openai/v1",
            default_model="openai/gpt-oss-120b",
        )