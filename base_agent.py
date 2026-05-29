import os
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()

class BaseAgent:
    def __init__(self, name, purpose, system_prompt):
        self.name = name
        self.purpose = purpose
        self.system_prompt = system_prompt
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError(f"MISTRAL_API_KEY not found for {self.name}")
        self.client = Mistral(api_key=api_key)
        self.model = "mistral-large-latest"

    def generate(self, user_prompt):
        print(f"[{self.name}] thinking...")
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        response = self.client.chat.complete(
            model=self.model,
            messages=messages,
        )
        return response.choices[0].message.content
