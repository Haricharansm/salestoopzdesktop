# agent/app/llm/ollama_client.py
import os
import json
import requests
from typing import Any, Optional

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
OLLAMA_PING_URL = os.getenv("OLLAMA_PING_URL", "http://127.0.0.1:11434")

# Use exact model names from `ollama list` (e.g., qwen2.5:3b)
MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

# Timeouts: keep reasonably high, but avoid huge prompts / num_predict to prevent hitting it.
DEFAULT_TIMEOUT_SECS = int(os.getenv("OLLAMA_TIMEOUT", "120"))

# For small local models on CPU, keep these modest to avoid long runs / truncation issues.
DEFAULT_NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "220"))
DEFAULT_REPAIR_NUM_PREDICT = int(os.getenv("OLLAMA_REPAIR_NUM_PREDICT", "80"))

# Optional: reduce randomness for JSON reliability
DEFAULT_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.1"))


def check_ollama() -> bool:
    try:
        r = requests.get(OLLAMA_PING_URL, timeout=2)
        return r.status_code == 200
    except Exception:
        return False


def warmup_ollama() -> None:
    """
    Pre-load the model so the first real request doesn't stall.
    Safe to call at startup.
    """
    try:
        _ = generate_text('{"warm":true}', temperature=0.0, num_predict=20)
    except Exception:
        # warmup should never crash app startup
        pass


def generate_text(prompt: str, temperature: float = DEFAULT_TEMPERATURE, num_predict: Optional[int] = None) -> str:
    if num_predict is None:
        num_predict = DEFAULT_NUM_PREDICT

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": float(temperature),
            "num_predict": int(num_predict),
        },
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=DEFAULT_TIMEOUT_SECS)
    except requests.exceptions.Timeout as e:
        raise Exception(f"Ollama request timed out after {DEFAULT_TIMEOUT_SECS}s") from e
    except Exception as e:
        raise Exception(f"Error calling Ollama at {OLLAMA_URL}: {e}") from e

    if response.status_code != 200:
        raise Exception(f"Error generating text (status={response.status_code}): {response.text}")

    data = response.json()
    return (data.get("response", "") or "").strip()


def _extract_first_json_object(text: str) -> Optional[str]:
    """
    Extract the first complete top-level JSON object by scanning braces,
    respecting strings/escapes. Returns None if no complete object found.
    """
    if not text:
        return None

    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    in_str = False
    esc = False

    for i in range(start, len(text)):
        ch = text[i]

        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue

        if ch == '"':
            in_str = True
            continue

        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]

    return None


def _auto_balance_json(text: str) -> Optional[str]:
    """
    If the model returned a truncated JSON object (missing closing braces/brackets),
    try to complete it by appending the needed closers.
    """
    if not text:
        return None

    start = text.find("{")
    if start == -1:
        return None

    s = text[start:].strip()

    open_curly = 0
    open_square = 0
    in_str = False
    esc = False

    for ch in s:
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue

        if ch == '"':
            in_str = True
            continue

        if ch == "{":
            open_curly += 1
        elif ch == "}":
            open_curly = max(0, open_curly - 1)
        elif ch == "[":
            open_square += 1
        elif ch == "]":
            open_square = max(0, open_square - 1)

    # can't safely repair if ended inside a string
    if in_str:
        return None

    s2 = s + ("]" * open_square) + ("}" * open_curly)

    end = s2.rfind("}")
    if end != -1:
        s2 = s2[: end + 1]

    return s2


def _strip_single_quote_wrappers(obj: Any) -> Any:
    """
    Converts strings like "'foo'" -> "foo" recursively.
    """
    if isinstance(obj, dict):
        return {k: _strip_single_quote_wrappers(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_strip_single_quote_wrappers(v) for v in obj]
    if isinstance(obj, str):
        s = obj.strip()
        if len(s) >= 2 and s[0] == "'" and s[-1] == "'":
            return s[1:-1].strip()
        return obj
    return obj


def generate_json(
    prompt: str,
    temperature: float = DEFAULT_TEMPERATURE,
    max_attempts: int = 3,
    num_predict: Optional[int] = None,
) -> dict:
    """
    Generate valid JSON from Ollama, with:
    - extraction of first JSON object
    - auto-balance repair for truncated JSON
    - LLM repair pass (SHORT INPUT, SHORT OUTPUT)
    - stripping of "'value'" wrappers
    """
    last_error = None
    last_raw = ""

    if num_predict is None:
        num_predict = DEFAULT_NUM_PREDICT

    # Always keep JSON generation deterministic-ish
    temperature = float(temperature)

    for attempt in range(1, max_attempts + 1):
        last_raw = generate_text(prompt, temperature=temperature, num_predict=num_predict)

        candidate = _extract_first_json_object(last_raw)
        if candidate is None:
            candidate = _auto_balance_json(last_raw) or last_raw.strip()

        # Parse attempt
        try:
            parsed = json.loads(candidate)
            return _strip_single_quote_wrappers(parsed)
        except Exception as e:
            last_error = f"[attempt {attempt}] {e}"

        # Repair pass: keep it SMALL so it doesn't time out
        short_input = candidate[-700:]  # prevent giant repair prompts on CPU
        repair_prompt = (
            "Fix into ONE valid JSON object. Return ONLY JSON.\n"
            "Use double quotes. Close all braces/brackets.\n"
            "Remove wrapping single quotes in values.\n"
            "INPUT:\n"
            f"{short_input}"
        )

        repaired_raw = generate_text(
            repair_prompt,
            temperature=0.0,
            num_predict=DEFAULT_REPAIR_NUM_PREDICT,
        )

        repaired_candidate = _extract_first_json_object(repaired_raw)
        if repaired_candidate is None:
            repaired_candidate = _auto_balance_json(repaired_raw) or repaired_raw.strip()

        try:
            parsed2 = json.loads(repaired_candidate)
            return _strip_single_quote_wrappers(parsed2)
        except Exception as e2:
            last_error = f"[attempt {attempt}] {e2}"

        # tighten prompt slightly and retry
        prompt = prompt + "\nReturn ONLY JSON. No extra text."

    preview = (last_raw or "")[:900]
    raise Exception(f"LLM did not return valid JSON. Last error: {last_error}. Raw preview: {preview}")
