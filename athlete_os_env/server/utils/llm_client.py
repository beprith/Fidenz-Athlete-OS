"""
OpenAI-compatible LLM wrapper.
Reads API_BASE_URL and MODEL_NAME from env vars.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from openai import OpenAI

from server.utils.logger import get_logger
from server.utils.retry import retry

log = get_logger("llm_client")


class LLMClient:
    """Thin wrapper around the OpenAI chat completions API."""

    def __init__(
        self,
        api_base_url: str | None = None,
        model_name: str | None = None,
        api_key: str | None = None,
    ):
        self.api_base_url = api_base_url or os.getenv("API_BASE_URL", "https://api.openai.com/v1")
        self.model_name = model_name or os.getenv("MODEL_NAME", "gpt-4o-mini")
        api_key = api_key or os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            log.warning("No API key found in HF_TOKEN or OPENAI_API_KEY env vars — LLM calls will fail")
            api_key = "sk-not-configured"
        self._client = OpenAI(api_key=api_key, base_url=self.api_base_url)

    @retry(max_retries=3, base_delay=1.0, exceptions=(Exception,))
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 1024,
        json_mode: bool = False,
    ) -> str:
        kwargs: Dict[str, Any] = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        completion = self._client.chat.completions.create(**kwargs)
        return completion.choices[0].message.content or ""

    def chat_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        text = self.chat(messages, temperature, max_tokens, json_mode=True)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            log.warning(f"LLM returned non-JSON: {text[:200]}")
            return {"raw": text}


_default_client: LLMClient | None = None


def get_llm_client() -> LLMClient:
    global _default_client
    if _default_client is None:
        _default_client = LLMClient()
    return _default_client
