"""
app/core/llm.py
Groq client with retry logic for all LLM agents.
"""
import json
import logging
import time
from typing import Type, TypeVar
from groq import Groq
from pydantic import BaseModel
from app.core.config import get_settings

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)

_MAX_RETRIES = 3
_RETRY_DELAY = 1.0


def _get_client() -> Groq:
    return Groq(api_key=get_settings().groq_api_key)


def chat_completion(
    messages: list[dict],
    model: str | None = None,
    temperature: float | None = None,
    json_mode: bool = False,
) -> str:
    cfg = get_settings()
    kwargs: dict = {
        "model": model or cfg.groq_model,
        "messages": messages,
        "temperature": temperature if temperature is not None else cfg.groq_temperature,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    client = _get_client()
    last_exc: Exception | None = None

    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content or ""
            print("[LLM] attempt=" + str(attempt) + " | model=" + str(kwargs["model"]) + " | chars=" + str(len(content)))
            print("[LLM RAW] " + content[:400])
            return content
        except Exception as exc:
            last_exc = exc
            print("[LLM] attempt=" + str(attempt) + " FAILED: " + str(exc))
            if attempt < _MAX_RETRIES:
                time.sleep(_RETRY_DELAY * attempt)

    raise RuntimeError("LLM call failed after " + str(_MAX_RETRIES) + " attempts: " + str(last_exc)) from last_exc


def chat_structured(
    messages: list[dict],
    output_model: Type[T],
    model: str | None = None,
    temperature: float | None = None,
) -> T:
    last_exc: Exception | None = None

    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            raw = chat_completion(messages, model=model, temperature=temperature, json_mode=True)

            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("```")[1]
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:]
                cleaned = cleaned.strip()

            data = json.loads(cleaned)
            result = output_model.model_validate(data)
            return result

        except Exception as exc:
            last_exc = exc
            print("[chat_structured] attempt=" + str(attempt) + " failed for " + output_model.__name__ + ": " + str(exc))
            if attempt < _MAX_RETRIES:
                time.sleep(_RETRY_DELAY)

    raise ValueError(
        "LLM response could not be parsed into " + output_model.__name__ + " after " + str(_MAX_RETRIES) + " attempts: " + str(last_exc)
    ) from last_exc
