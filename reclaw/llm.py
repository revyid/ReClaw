from openai import OpenAI
from .config import NVIDIA_BASE_URL, NVIDIA_API_KEY, MODEL_NAME

class LLMClient:
    def __init__(self):
        if not NVIDIA_API_KEY:
            raise ValueError("API Key tidak ditemukan. Set environment variable RECLAW_API_KEY.")
        self.client = OpenAI(
            base_url=NVIDIA_BASE_URL,
            api_key=NVIDIA_API_KEY
        )
        self.model = MODEL_NAME

    def chat(self, messages, tools=None, tool_choice="auto"):
        """Kirim request ke NVIDIA API."""
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = tool_choice

        try:
            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message
        except Exception as e:
            return {"role": "assistant", "content": f"Error API: {str(e)}"}
