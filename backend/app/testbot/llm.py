import os
import json
import requests
import logging
from typing import Dict, Any, Optional
from config import GEMINI_API_URL

# Configure logging
logger = logging.getLogger(__name__)

def create_prompt(query: str, context_docs: list) -> str:
    """Create a structured prompt for the LLM"""
    context_text = "\n\n".join([f"Document {i+1}:\n{doc}" for i, doc in enumerate(context_docs)])
    
    prompt = f"""You are a helpful AI assistant providing accurate answers based on the provided context. 
If the answer isn't found in the context, politely say you don't know instead of making up information.

## CONTEXT:
{context_text}

## QUESTION:
{query}

## ANSWER:
"""
    return prompt

def ask_llm(prompt: str) -> str:
    """Send a prompt to the Gemini API and get a response"""
    try:
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 1024,
                "topP": 0.95,
                "topK": 40
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(GEMINI_API_URL, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            response_data = response.json()
            text = response_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            return text
        else:
            logger.error(f"API request failed with status {response.status_code}: {response.text}")
            return f"Error: Failed to get response from LLM (Status {response.status_code})"
    
    except Exception as e:
        logger.error(f"Error in LLM request: {e}")
        return f"Error: {str(e)}"

def process_query(chatbot_id: str, query: str, context_docs: list) -> str:
    """Process a query using the appropriate context and LLM"""
    prompt = create_prompt(query, context_docs)
    logger.info(f"Sending prompt to LLM for chatbot {chatbot_id}")
    response = ask_llm(prompt)
    return response