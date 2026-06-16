"""LLM abstraction layer for iFin.

This service supports an OpenAI-compatible chat completions endpoint through
environment variables. If configuration is missing or a request fails, it
returns a safe placeholder string so the app can fall back to the mock pipeline.
"""

from __future__ import annotations

import os
from typing import Any

import requests

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dependency is listed in requirements.
    load_dotenv = None


PLACEHOLDER_MESSAGE = "LLM integration not enabled yet"


class LLMService:
    """Service boundary for future DeepSeek/OpenRouter compatible calls."""

    def __init__(self) -> None:
        if load_dotenv is not None:
            load_dotenv()

        self.provider = os.getenv("IFIN_LLM_PROVIDER", "").strip()
        self.api_key = os.getenv("IFIN_LLM_API_KEY", "").strip()
        self.base_url = os.getenv("IFIN_LLM_BASE_URL", "").strip().rstrip("/")
        self.model = os.getenv("IFIN_LLM_MODEL", "").strip()

    def _is_configured(self) -> bool:
        """Return whether a real OpenAI-compatible LLM call can be attempted."""
        return bool(
            self.provider == "openai-compatible"
            and self.api_key
            and self.base_url
            and self.model
        )

    def _chat_completions_url(self) -> str:
        """Build the OpenAI-compatible chat completions URL."""
        if self.base_url.endswith("/v1"):
            return f"{self.base_url}/chat/completions"
        return f"{self.base_url}/v1/chat/completions"

    def analyze_event(self, prompt: str) -> str:
        """Analyze an event prompt and return raw LLM text.

        Future versions may support multiple providers. For now, only
        OpenAI-compatible chat completions are supported. Missing config or any
        request failure returns a placeholder string instead of raising.
        """
        if not self._is_configured():
            return PLACEHOLDER_MESSAGE

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "temperature": 0.2,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                self._chat_completions_url(),
                headers=headers,
                json=payload,
                timeout=45,
            )
            response.raise_for_status()
            data = response.json()
            choices = data.get("choices") or []
            if not choices:
                return PLACEHOLDER_MESSAGE
            message = choices[0].get("message") or {}
            content = message.get("content")
            return content if isinstance(content, str) and content.strip() else PLACEHOLDER_MESSAGE
        except Exception:
            return PLACEHOLDER_MESSAGE


if __name__ == "__main__":
    llm = LLMService()

    result = llm.analyze_event(
        "请用一句话解释：美联储降息50bp可能如何影响市场风险偏好。"
    )

    print(result)
