import requests
import os
import sys

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_URL = f"{OLLAMA_HOST}/api/generate"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from system_prompts import SYSTEM_PROMPTS_MAP
except ImportError:
    print("[ERROR] Could not import SYSTEM_PROMPTS_MAP from system_prompts.py. "
          "Please ensure system_prompts.py exists in the same directory and defines SYSTEM_PROMPTS_MAP.", file=sys.stderr)
    sys.exit(1)


def generate_professor_lecture(notes: str, ollama_model_name: str, system_prompt_type: str) -> str:
    system_prompt = SYSTEM_PROMPTS_MAP.get(system_prompt_type)

    if not system_prompt:
        return f"[ERROR] Invalid system_prompt_type: '{system_prompt_type}'. " \
               f"Available types: {list(SYSTEM_PROMPTS_MAP.keys())}"

    payload = {
        "model": ollama_model_name,
        "prompt": f"{system_prompt}\n\nLecture Notes:\n{notes}\n\nLecture Script:",
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        return response.json()["response"].strip()
    
    except requests.exceptions.ConnectionError:
        return f"[ERROR] Could not connect to Ollama at {OLLAMA_URL}. Is Ollama running and accessible?"
    except requests.RequestException as e:
        return f"[ERROR] Failed with model '{ollama_model_name}' and prompt type '{system_prompt_type}': {e}"
    except KeyError:
        return f"[ERROR] Unexpected response format from Ollama. Response: {response.text}"

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python generate_lecture.py <notes_text> <ollama_model_name> <system_prompt_type>", file=sys.stderr)
        sys.exit(1)
    
    notes_text = sys.argv[1]
    ollama_model_name = sys.argv[2]
    system_prompt_type = sys.argv[3]
    
    try:
        generated_lecture = generate_professor_lecture(notes_text, ollama_model_name, system_prompt_type)
        print(generated_lecture)
    except Exception as e:
        print(f"Error during lecture generation: {e}", file=sys.stderr)
        sys.exit(1)
