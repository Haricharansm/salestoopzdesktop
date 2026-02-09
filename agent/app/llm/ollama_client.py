import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

def check_ollama():
    try:
        response = requests.get("http://127.0.0.1:11434")
        return response.status_code == 200
    except:
        return False

def generate_text(prompt):
    payload = {
        "model": "llama3.1",
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)

    if response.status_code == 200:
        return response.json()["response"]
    else:
        return "Error generating text"
