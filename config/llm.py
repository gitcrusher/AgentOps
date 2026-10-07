"""Provider-agnostic LLM call layer (AGENTS.md Section 7).

Agents call `chat(...)` and never touch a provider SDK directly, so switching
between Groq and Gemini is a config change (LLM_PROVIDER), not a code change.

Retry policy (AGENTS.md Section 2): on failure/timeout/rate-limit, retry once
after a 2s backoff; if it fails again, raise LLMUnavailable so the caller can
return its `llm_unavailable` failure output and route to escalation.
"""
import os
import time

from config.settings import (
    LLM_PROVIDER,
    GROQ_MODEL,
    GEMINI_MODEL,
    LLM_TIMEOUT_SECONDS,
    LLM_RETRY_BACKOFF_SECONDS,
)


class LLMUnavailable(Exception):
    """Raised when the LLM call fails after the single allowed retry."""


def _call_groq(system, user, temperature, max_tokens, json_mode):
    from groq import Groq

    client = Groq(api_key=os.getenv("GROQ_API_KEY"), timeout=LLM_TIMEOUT_SECONDS)
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})
    kwargs = dict(
        messages=messages,
        model=GROQ_MODEL,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content


def _call_gemini(system, user, temperature, max_tokens, json_mode):
    from google import genai
    from google.genai import types

    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY"),
        http_options=types.HttpOptions(timeout=LLM_TIMEOUT_SECONDS * 1000),
    )
    config = types.GenerateContentConfig(
        system_instruction=system or None,
        temperature=temperature,
        max_output_tokens=max_tokens,
        response_mime_type="application/json" if json_mode else None,
    )
    response = client.models.generate_content(
        model=GEMINI_MODEL, contents=user, config=config
    )
    return response.text


def chat(system: str, user: str, *, temperature: float, max_tokens: int,
         json_mode: bool = False) -> str:
    """Single LLM completion with one retry. Raises LLMUnavailable on failure."""
    if LLM_PROVIDER == "groq":
        call = _call_groq
    elif LLM_PROVIDER == "gemini":
        call = _call_gemini
    else:
        raise LLMUnavailable(f"unknown LLM_PROVIDER: {LLM_PROVIDER}")

    last_error = None
    for attempt in range(2):
        try:
            return call(system, user, temperature, max_tokens, json_mode)
        except Exception as e:  # network, timeout, rate limit, bad response
            last_error = e
            # Don't retry errors that can't succeed on retry (bad key/model).
            msg = str(e).lower()
            if any(s in msg for s in ("401", "403", "404", "invalid api key", "decommissioned", "not_found")):
                break
            if attempt == 0:
                time.sleep(LLM_RETRY_BACKOFF_SECONDS)
    # Provider error messages (e.g. "model decommissioned") are kept for debugging;
    # they don't contain the API key, which is only ever sent as a request header.
    raise LLMUnavailable(f"{LLM_PROVIDER} call failed: {type(last_error).__name__}: {last_error}")
