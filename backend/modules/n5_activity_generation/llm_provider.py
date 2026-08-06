"""
providers.py — LLM provider layer (Groq).

Procedural Architecture:
  - 1 provider = 1 config dict: {"name", "model", "rpm_limit", "call_fn", "key_fn"}
  - generate(provider, prompt, ...) handles: retry, backoff, logging
  - _call_groq(...) performs the actual HTTP call for Groq, raising RetryableError
    for temporary failures (429, 503, timeout) so generate() can retry.
"""

from __future__ import annotations

import json
import random
import time
import urllib.error
import urllib.request
from typing import Callable, Dict, List, Optional

from config import (
    setup_logging,
    GROQ_API_KEY,
)
from .config import (
    MAX_RETRIES, 
    RETRY_WAIT_BASE, 
    LLM_TEMP,
    GROQ_API_URL,
    GROQ_MODELS,
    LLM_CHAIN,
    USER_AGENT,
)
logger = setup_logging("N5.provider")


class RetryableError(Exception):
    """Temporary error (429/503/timeout) — generate() will retry with backoff."""

    def __init__(self, message: str, status: Optional[int] = None):
        super().__init__(message)
        self.status = status


# Stores token usage per provider to track state without OOP.
_LAST_USAGE: Dict[str, dict] = {}

DEFAULT_SYSTEM = (
    "You are a travel expert. Always respond with pure JSON only — "
    "no markdown, no code blocks, no explanation. Start your response directly with ["
)


# ── Groq call implementation ────────────────────────────────────────────────

def _groq_api_key() -> Optional[str]:
    # Lazy import to allow env reload.
    from config import GROQ_API_KEY as _KEY
    return _KEY


def _call_groq(
    provider: dict,
    prompt: str,
    system: Optional[str] = None,
    max_tokens: int = 4096,
) -> Optional[str]:
    """
    Execute a single HTTP call to Groq (no retry).

    Return: text response from model (unparsed JSON).
    Raise RetryableError for: 429, 503, timeout, connection reset.
    Return None for: non-retryable errors (auth, bad request, parse error).
    """
    payload = {
        "model": provider["model"],
        "messages": [
            {"role": "system", "content": system or DEFAULT_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        "temperature": LLM_TEMP,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"},
    }
    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        GROQ_API_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {_groq_api_key()}",
            "User-Agent": USER_AGENT,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=provider.get("timeout", 60)) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code in (429, 503, 502, 504):
            raise RetryableError(f"Groq HTTP {e.code}", status=e.code) from e
        try:
            body = e.read().decode("utf-8", errors="replace")[:400]
        except Exception:
            body = ""
        logger.error("Groq HTTP %s non-retryable: %s", e.code, body)
        return None
    except (urllib.error.URLError, TimeoutError) as e:
        raise RetryableError(f"Groq network error: {e}") from e

    choices = result.get("choices", [])
    usage = result.get("usage", {})
    if usage:
        p_tokens = usage.get("prompt_tokens", 0)
        c_tokens = usage.get("completion_tokens", 0)
        _LAST_USAGE[provider["name"]] = {"prompt_tokens": p_tokens, "completion_tokens": c_tokens}
        logger.info("Groq usage: %d prompt, %d completion tokens", p_tokens, c_tokens)

    if choices:
        return choices[0].get("message", {}).get("content", "")

    logger.warning("Groq response format unexpected: %s", str(result)[:200])
    return None


# ── Provider factory ────────────────────────────────────────────────────────

def _make_provider(name: str, model: str, call_fn: Callable, key_fn: Callable, rpm_limit: int = 30) -> dict:
    return {
        "name": name,
        "model": model,
        "rpm_limit": rpm_limit,
        "call_fn": call_fn,
        "key_fn": key_fn,
    }


def _resolve_provider(name: str) -> Optional[dict]:
    """Create a provider dict by name. Supports Groq aliases."""
    name = name.strip().lower()

    if name in GROQ_MODELS:
        return _make_provider(name, GROQ_MODELS[name], _call_groq, _groq_api_key)

    logger.warning("Unknown provider '%s', skipping", name)
    return None


def is_available(provider: dict) -> bool:
    """Provider is ready if API key is present."""
    key = provider["key_fn"]()
    return bool(key and key.strip())


def get_last_usage(provider: dict) -> Optional[dict]:
    """Token usage of the last generate() call for this provider."""
    return _LAST_USAGE.get(provider["name"])


# ── generate(): retry + backoff ─────────────────────────────────────────────

def generate(
    provider: dict,
    prompt: str,
    system: Optional[str] = None,
    max_tokens: int = 4096,
) -> Optional[str]:
    """
    Call LLM with exponential backoff + jitter.

    wait = min(30, 2^attempt + random(0, 1)) seconds.

    Return text response or None if failed after all retries.
    """
    name = provider["name"]
    model = provider["model"]

    if not is_available(provider):
        logger.debug("Provider %s unavailable (missing API key)", name)
        return None

    t0 = time.time()
    try:
        result = provider["call_fn"](
            provider,
            prompt=prompt,
            system=system,
            max_tokens=max_tokens,
        )
        latency_ms = int((time.time() - t0) * 1000)
        if result:
            logger.info(
                "LLM call provider=%s model=%s status=ok latency_ms=%d",
                name, model, latency_ms,
            )
            return result
        # call_fn returns None = non-retryable error (auth, parse, safety)
        logger.warning(
            "LLM call provider=%s model=%s status=fail_nonretryable latency_ms=%d",
            name, model, latency_ms,
        )
        return None

    except RetryableError as e:
        latency_ms = int((time.time() - t0) * 1000)
        logger.warning(
            "LLM call provider=%s model=%s status=retryable_%s latency_ms=%d",
            name, model, e.status, latency_ms,
        )
        raise e

    except Exception as e:
        latency_ms = int((time.time() - t0) * 1000)
        logger.error(
            "LLM call provider=%s model=%s status=error latency_ms=%d err=%s",
            name, model, latency_ms, e,
        )
        return None


# ── Chain / registry helpers ────────────────────────────────────────────────

def get_provider(name: Optional[str] = None) -> Optional[dict]:
    """Get a provider by name."""
    if name:
        return _resolve_provider(name)

    # If no name is provided, return the first provider in LLM_CHAIN
    chain_names = [n.strip() for n in LLM_CHAIN.split(",") if n.strip()]
    if chain_names:
        return _resolve_provider(chain_names[0])

    logger.error("LLM_CHAIN empty and no provider name specified. Cannot get a provider.")
    return None


def get_llm_chain(chain_str: Optional[str] = None) -> List[dict]:
    """
    Build a chain from LLM_CHAIN, keeping only providers with an API key.

    Args:
      chain_str: Comma-separated string of model names. Default = config.LLM_CHAIN.

    Returns the filtered list; may be empty if no providers have keys.
    """
    raw_str = chain_str if chain_str is not None else LLM_CHAIN
    names = [n.strip() for n in raw_str.split(",") if n.strip()]

    # Deduplicate while preserving order
    seen = set()
    ordered = []
    for n in names:
        key = n.lower()
        if key and key not in seen:
            seen.add(key)
            ordered.append(key)

    chain: List[dict] = []
    for name in ordered:
        provider = _resolve_provider(name)
        if provider is None:
            continue
        if not is_available(provider):
            logger.info("Provider '%s' is in chain but missing API key — skipping", name)
            continue
        chain.append(provider)

    if not chain:
        logger.error("No available providers — check GROQ_API_KEY")

    return chain


def available_providers() -> List[str]:
    """Return names of registered providers."""
    return list(GROQ_MODELS.keys())