import requests
from typing import Dict, Any, Optional

from core.config import FREE_LLM_API_URL, FREE_LLM_API_KEY, FREE_LLM_PROVIDER
from core.logger import logger

def format_with_huggingface(prompt: str) -> str:
    """Format response using HuggingFace Inference API"""
    headers = {
        "Authorization": f"Bearer {FREE_LLM_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_length": 102400,
            "temperature": 0.7,
            "top_p": 0.9
        }
    }
    
    response = requests.post(
        FREE_LLM_API_URL,
        headers=headers,
        json=payload
    )
    
    if response.status_code == 200:
        return response.json()[0]["generated_text"]
    else:
        raise Exception(f"HuggingFace API error: {response.status_code} - {response.text}")

def format_with_ollama(prompt: str) -> str:
    """Format response using local Ollama instance"""
    payload = {
        "model": "llama2",
        "prompt": prompt,
        "stream": False
    }
    
    response = requests.post(
        FREE_LLM_API_URL,
        json=payload
    )
    
    if response.status_code == 200:
        return response.json()["response"]
    else:
        raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
    
async def format_response(raw_response: str, query: str) -> str:
    """Format the response using a free LLM"""
    try:
        # Create a prompt for the formatting LLM
        prompt = f"""
        Please format the following AI response to make it more concise, clear, and user-friendly.
        
        Original user query: {query}
        
        Raw AI response:
        {raw_response}
        
        Formatted response:
        """
        
        # Choose the appropriate formatter based on the configured provider
        formatters = {
            "huggingface": format_with_huggingface,
        }
        
        formatter = formatters.get(FREE_LLM_PROVIDER, format_with_huggingface)
        formatted_text = formatter(prompt)
        
        logger.info(f"Response successfully formatted with {FREE_LLM_PROVIDER}")
        return formatted_text
        
    except Exception as e:
        logger.error(f"Error formatting response with {FREE_LLM_PROVIDER}: {e}")
        return raw_response  # Fall back to raw response if formatting fails