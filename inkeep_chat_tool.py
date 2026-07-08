#!/usr/bin/env python3
"""Hermes Agent Tool: ask Inkeep to fix a Python snippet.

The tool intentionally reads the bearer token from INKEEP_BEARER_TOKEN only.
It never stores credentials in source files or in the tool response.
"""

import base64
import hashlib
import json
import os
import time
from typing import Any, Dict

import requests

from tools.registry import registry, tool_error, tool_result

CHALLENGE_URL = "https://api.inkeep.com/v1/challenge"
COMPLETIONS_URL = "https://api.inkeep.com/v1/chat/completions"
DEFAULT_MODEL = "inkeep-qa-expert"
DEFAULT_TIMEOUT_SECONDS = 15


def _solve_pow(challenge_data: Dict[str, Any]) -> int:
    algorithm = str(challenge_data.get("algorithm", "SHA-256")).upper()
    if algorithm != "SHA-256":
        raise ValueError(f"Unsupported challenge algorithm: {algorithm}")

    salt = challenge_data["salt"]
    target = challenge_data["challenge"]
    max_number = int(challenge_data.get("maxnumber", 50000))

    for number in range(max_number + 1):
        digest = hashlib.sha256(f"{salt}{number}".encode("utf-8")).hexdigest()
        if digest == target:
            return number

    raise RuntimeError("Could not solve Inkeep PoW challenge in the provided range.")


def _build_headers(token: str, challenge_solution: str | None = None) -> Dict[str, str]:
    headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "origin": "https://platform.claude.com",
        "referer": "https://platform.claude.com/",
        "user-agent": "Mozilla/5.0",
    }
    if token:
        headers["authorization"] = token
    if challenge_solution:
        headers["x-inkeep-challenge-solution"] = challenge_solution
    return headers


def _get_challenge_solution(token: str, timeout_seconds: int) -> tuple[str, float]:
    started = time.perf_counter()
    response = requests.get(CHALLENGE_URL, headers=_build_headers(token), timeout=timeout_seconds)
    response.raise_for_status()
    challenge_data = response.json()
    challenge_data["number"] = _solve_pow(challenge_data)
    encoded = base64.b64encode(json.dumps(challenge_data).encode("utf-8")).decode("utf-8")
    return encoded, time.perf_counter() - started


def _clean_timeout(value: Any) -> int:
    try:
        timeout = int(value)
    except Exception:
        timeout = DEFAULT_TIMEOUT_SECONDS
    return max(5, min(timeout, 60))


def inkeep_fix_python_code(
    code: str,
    instruction: str | None = None,
    model: str = DEFAULT_MODEL,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> str:
    if not code or not code.strip():
        return tool_error("code argument is required.")

    token = os.environ.get("INKEEP_BEARER_TOKEN")
    if not token:
        return tool_error("Missing INKEEP_BEARER_TOKEN environment variable.")

    timeout_seconds = _clean_timeout(timeout_seconds)
    prompt = instruction or "Fix this Python code. Return only the corrected Python code."
    payload = {
        "model": model or DEFAULT_MODEL,
        "stream": False,
        "messages": [
            {
                "role": "user",
                "content": f"{prompt}\n\n```python\n{code}\n```",
            }
        ],
    }

    total_started = time.perf_counter()
    try:
        challenge_solution, challenge_seconds = _get_challenge_solution(token, timeout_seconds)
        headers = _build_headers(token, challenge_solution)

        request_started = time.perf_counter()
        response = requests.post(COMPLETIONS_URL, headers=headers, json=payload, timeout=timeout_seconds)
        request_seconds = time.perf_counter() - request_started
        response.raise_for_status()

        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        usage = data.get("usage", {})
        timings = {
            "challenge_seconds": round(challenge_seconds, 3),
            "request_seconds": round(request_seconds, 3),
            "total_seconds": round(time.perf_counter() - total_started, 3),
        }
        return tool_result({"content": content, "model": data.get("model"), "usage": usage, "timings": timings})
    except requests.Timeout:
        elapsed = round(time.perf_counter() - total_started, 3)
        return tool_error(f"Inkeep request timed out after {elapsed}s. Try a shorter prompt or timeout_seconds=30.")
    except requests.HTTPError as e:
        status = e.response.status_code if e.response is not None else "unknown"
        body = e.response.text[:500] if e.response is not None else ""
        return tool_error(f"Inkeep HTTP error {status}: {body}")
    except Exception as e:
        return tool_error(f"Inkeep request failed: {type(e).__name__}: {e}")


INKEEP_FIX_PYTHON_SCHEMA = {
    "name": "inkeep_fix_python_code",
    "description": (
        "Send a Python snippet to Inkeep and ask for a corrected version. "
        "Requires INKEEP_BEARER_TOKEN in the environment; credentials are never stored in files. "
        "Returns timing diagnostics so slow calls can be identified."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "The Python code snippet to fix.",
            },
            "instruction": {
                "type": "string",
                "description": "Optional custom instruction for the fix request.",
            },
            "model": {
                "type": "string",
                "description": "Optional Inkeep model name. Defaults to inkeep-qa-expert.",
            },
            "timeout_seconds": {
                "type": "integer",
                "description": "Request timeout in seconds, from 5 to 60. Defaults to 15.",
            },
        },
        "required": ["code"],
    },
}


registry.register(
    name="inkeep_fix_python_code",
    toolset="file",
    schema=INKEEP_FIX_PYTHON_SCHEMA,
    handler=lambda args, **kw: inkeep_fix_python_code(
        code=args.get("code", ""),
        instruction=args.get("instruction"),
        model=args.get("model", DEFAULT_MODEL),
        timeout_seconds=args.get("timeout_seconds", DEFAULT_TIMEOUT_SECONDS),
    ),
    check_fn=lambda: bool(os.environ.get("INKEEP_BEARER_TOKEN")),
    emoji="🔧",
)
