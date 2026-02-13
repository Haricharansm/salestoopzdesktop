import os
import json
import requests

# -----------------------------
# Ollama Configuration
# -----------------------------

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_PING_URL = "http://127.0.0.1:11434"

MODEL_NAME = os.getenv("OLLAMA_MODEL", "mistral:latest")

DEFAULT_TIMEOUT_SECS = int(os.getenv("OLLAMA_TIMEOUT", "300"))
DEFAULT_NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "450"))


# -----------------------------
# Health Check
# -----------------------------
def check_ollama() -> bool:
    try:
        r = requests.get(OLLAMA_PING_URL, timeout=3)
        return r.status_code == 200
    except Exception:
        return False


# -----------------------------
# Text Generation
# -----------------------------
def generate_text(
    prompt: str,
    temperature: float = 0.2,
    num_predict: int | None = None,
) -> str:
    """
    Generate raw text from Ollama
    """

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
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=DEFAULT_TIMEOUT_SECS,
        )
    except requests.exceptions.Timeout as e:
        raise Exception(
            f"Ollama request timed out after {DEFAULT_TIMEOUT_SECS}s"
        ) from e
    except Exception as e:
        raise Exception(f"Error calling Ollama at {OLLAMA_URL}: {e}") from e

    if response.status_code != 200:
        raise Exception(
            f"Ollama error (status={response.status_code}): {response.text}"
        )

    data = response.json()
    return data.get("response", "") or ""


# -----------------------------
# JSON Extraction Helper
# -----------------------------
def _extract_json_object(text: str) -> str | None:
    """
    Extract first valid top-level JSON object from model output.
    Handles cases where model adds explanation text.
    """

    if not text:
        return None

    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    in_string = False
    escape = False

    for i in range(start, len(text)):
        ch = text[i]

        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
            continue

        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1

            if depth == 0:
                return text[start : i + 1]

    return None


# -----------------------------
# JSON Generation Wrapper
# -----------------------------
def generate_json(
    prompt: str,
    temperature: float = 0.2,
    max_attempts: int = 3,
    num_predict: int | None = None,
) -> dict:
    """
    Generate STRICT valid JSON using:
    - Extraction pass
    - Repair pass
    - Retry tightening prompt
    """

    np = num_predict if num_predict is not None else DEFAULT_NUM_PREDICT
    last_error = None
    last_raw = ""

    for attempt in range(1, max_attempts + 1):

        # ---------------- First Attempt ----------------
        last_raw = generate_text(
            prompt,
            temperature=temperature,
            num_predict=np,
        )

        candidate = _extract_json_object(last_raw) or last_raw.strip()

        try:
            return json.loads(candidate)
        except Exception as e:
            last_error = f"[attempt {attempt}] {str(e)}"

        # ---------------- Repair Attempt ----------------
        repair_prompt = f"""
You are a strict JSON formatter.

Fix the following so it becomes ONE valid JSON object.
Return ONLY the corrected JSON. No explanation. No markdown.

INVALID_JSON:
{candidate}
"""

        repaired_raw = generate_text(
            repair_prompt,
            temperature=0.0,
            num_predict=np,
        )

        candidate2 = _extract_json_object(repaired_raw) or repaired_raw.strip()

        try:
            return json.loads(candidate2)
        except Exception as e:
            last_error = f"[attempt {attempt} repair] {str(e)}"

        # Tighten instructions
        prompt += "\n\nReturn ONLY valid JSON. Do not include any explanation."

    preview = (last_raw or "")[:800]

    raise Exception(
        f"LLM did not return valid JSON. Last error: {last_error}. Raw preview: {preview}"
    )
