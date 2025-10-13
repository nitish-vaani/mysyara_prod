from openai import OpenAI
from typing import Optional

class LLMPromptRunner:
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def run_prompt(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Runs a prompt using OpenAI's v1 ChatCompletion API with 'gpt-4o' or other chat models.

        Parameters:
        - prompt: Full text prompt for the user role.
        - system_message: Optional system prompt to define assistant behavior.
        - temperature: Controls randomness.
        - max_tokens: Optional limit for output tokens.

        Returns:
        - Model's output as a string.
        """
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()
