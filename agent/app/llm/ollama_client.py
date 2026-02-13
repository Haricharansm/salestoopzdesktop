import requests
import json
import re

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "llama3.1"


def check_ollama():
    try:
        response = requests.get("http://127.0.0.1:11434")
        return response.status_code == 200
    except:
        return False


def generate_text(prompt: str, temperature: float = 0.4) -> str:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature
        }
    }

    response = requests.post(OLLAMA_URL, json=payload)

    if response.status_code == 200:
        return response.json().get("response", "")
    else:
        raise Exception(f"Error generating text (status={response.status_code}): {response.text}")


def generate_json(prompt: str, temperature: float = 0.35, retries: int = 2) -> dict:
    """
    Stronger helper for agents: returns dict, retries, extracts JSON if model adds extra text.
    """
    last_err = None
    for _ in range(retries):
        raw = generate_text(prompt, temperature=temperature)
        try:
            return json.loads(raw)
        except Exception as e:
            last_err = e
            extracted = _extract_json_block(raw)
            if extracted is not None:
                return extracted

    raise Exception(f"LLM did not return valid JSON. Last error: {last_err}")


def _extract_json_block(text: str):
    """
    Tries to find the first {...} JSON object in the output.
    """
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except:
        return None
