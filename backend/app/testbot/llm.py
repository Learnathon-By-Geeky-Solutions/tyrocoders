# llm.py
import json
import requests
from config import GEMINI_API_URL

def ask_llm(prompt):
    """
    Given a prompt, call the Gemini API and return the generated answer.
    """
    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(GEMINI_API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        try:
            result = response.json()
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    answer_text = candidate["content"]["parts"][0].get("text", "").strip()
                    return answer_text if answer_text else "No output returned."
                else:
                    return "No content found in candidate."
            else:
                return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error parsing response: {e}"
    else:
        return f"Error: {response.status_code} {response.text}"
