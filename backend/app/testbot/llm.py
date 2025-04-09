import os
import json
import requests
import logging
import re
from typing import Dict, Any, List, Optional
from config import GEMINI_API_URL

# Configure logging
logger = logging.getLogger(__name__)

def create_prompt(query: str, context_docs: list, conversation_history=None) -> str:
    """Create a structured prompt for the LLM optimized for product queries"""
    # Filter and prioritize most relevant context documents
    prioritized_docs = prioritize_context_docs(query, context_docs)
    
    # Format context in a concise way
    context_text = "\n\n".join([f"Document {i+1}:\n{doc}" for i, doc in enumerate(prioritized_docs)])
    
    # Add conversation history if available, limited to recent exchanges
    history_text = ""
    if conversation_history and len(conversation_history) > 0:
        recent_history = conversation_history[-3:]  # Last 3 exchanges
        history_text = "## CONVERSATION HISTORY:\n" + "\n".join([
            f"User: {exchange['query']}\nAssistant: {summarize_response(exchange['response'])}" 
            for exchange in recent_history
        ]) + "\n\n"
    
    # Different prompt templates based on query type
    if is_product_query(query):
        prompt = f"""You are a helpful AI product assistant. Answer user queries about products based on the provided context.
If the answer isn't found in the context, politely say you don't know instead of making up information.

For product queries, output your response in the following JSON format:
```json
{{
  "product_name": "Name of the product",
  "product_description": "Brief description of the product",
  "price": "Price information if available",
  "url": "URL to the product if available",
  "availability": "Availability information if available",
  "related_products": ["Related product 1", "Related product 2"],
  "answer": "Your complete natural language answer here"
}}
```

{history_text}## CONTEXT:
{context_text}

## CURRENT QUESTION:
{query}

## RESPONSE:
"""
    else:
        # Simpler prompt for non-product queries to save tokens
        prompt = f"""Answer the question based on the provided context. Be concise.
If you don't find the answer in the context, simply say you don't know.

{history_text}## CONTEXT:
{context_text}

## QUESTION:
{query}

## ANSWER:
"""
    return prompt

def prioritize_context_docs(query: str, context_docs: list) -> list:
    """Filter and prioritize context documents based on relevance to query"""
    if len(context_docs) <= 5:
        return context_docs
    
    # Simple keyword matching for prioritization
    # In production, use a better relevance scoring method
    query_keywords = set(query.lower().split())
    
    # Score documents by keyword matches
    scored_docs = []
    for doc in context_docs:
        doc_lower = doc.lower()
        score = sum(1 for keyword in query_keywords if keyword in doc_lower)
        scored_docs.append((score, doc))
    
    # Sort by score (descending) and take top 5
    sorted_docs = [doc for _, doc in sorted(scored_docs, key=lambda x: x[0], reverse=True)]
    return sorted_docs[:5]

def summarize_response(response: str, max_length=100) -> str:
    """Summarize a response to reduce token usage in history"""
    # If response is JSON, extract just the "answer" field
    if response.strip().startswith('{') and response.strip().endswith('}'):
        try:
            response_data = json.loads(response)
            if "answer" in response_data:
                response = response_data["answer"]
        except:
            pass
    
    # If response is too long, truncate it
    if len(response) > max_length:
        return response[:max_length] + "..."
    return response

def is_product_query(query: str) -> bool:
    """Determine if a query is about products"""
    product_indicators = [
        "product", "buy", "purchase", "price", "cost", "how much", 
        "where can I get", "looking for", "search for", "find", 
        "show me", "available", "stock", "shipping", "delivery"
    ]
    
    query_lower = query.lower()
    return any(indicator in query_lower for indicator in product_indicators)

def ask_llm(prompt: str) -> str:
    """Send a prompt to the Gemini API and get a response"""
    try:
        # Estimate token count to avoid exceeding limits
        estimated_tokens = estimate_token_count(prompt)
        logger.info(f"Estimated prompt tokens: {estimated_tokens}")
        
        # If prompt is too large, reduce it
        if estimated_tokens > 2000:
            logger.warning("Prompt too large, reducing context")
            prompt = reduce_prompt_size(prompt)
        
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

def estimate_token_count(text: str) -> int:
    """Estimate the number of tokens in a text
    This is a simple approximation - 4 chars ~= 1 token for English text"""
    return len(text) // 4

def reduce_prompt_size(prompt: str) -> str:
    """Reduce the size of the prompt to avoid token limits"""
    # Extract the sections
    sections = {}
    current_section = "preamble"
    sections[current_section] = []
    
    for line in prompt.split('\n'):
        if line.startswith('## '):
            current_section = line[3:].strip()
            sections[current_section] = []
        else:
            sections.get(current_section, []).append(line)
    
    # If context section exists and is large, reduce it
    if "CONTEXT" in sections and len(sections["CONTEXT"]) > 20:
        # Keep only first few documents
        context_lines = sections["CONTEXT"]
        doc_starts = [i for i, line in enumerate(context_lines) if line.startswith("Document ")]
        
        if len(doc_starts) > 3:
            # Keep only first 3 documents
            if len(doc_starts) > 3:
                keep_until = doc_starts[3] if len(doc_starts) > 3 else len(context_lines)
                sections["CONTEXT"] = context_lines[:keep_until]
    
    # Reconstruct the prompt
    reduced_prompt = []
    for section, lines in sections.items():
        if section == "preamble":
            reduced_prompt.extend(lines)
        else:
            reduced_prompt.append(f"## {section}")
            reduced_prompt.extend(lines)
    
    return "\n".join(reduced_prompt)

def process_query(chatbot_id: str, query: str, context_docs: list, conversation_history=None) -> str:
    """Process a query using the appropriate context and LLM"""
    prompt = create_prompt(query, context_docs, conversation_history)
    logger.info(f"Sending prompt to LLM for chatbot {chatbot_id}")
    response = ask_llm(prompt)
    
    # Log token usage for monitoring
    prompt_tokens = estimate_token_count(prompt)
    response_tokens = estimate_token_count(response)
    logger.info(f"Token usage - Prompt: {prompt_tokens}, Response: {response_tokens}, Total: {prompt_tokens + response_tokens}")
    
    return response