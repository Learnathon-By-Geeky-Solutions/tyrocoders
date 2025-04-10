import os
import json
import requests
import logging
import re
from typing import Dict, Any, List, Optional
from config import GEMINI_API_URL

logger = logging.getLogger(__name__)

def create_prompt(query: str, context_docs: list, conversation_history=None) -> str:
    """Create prompt for the LLM based on product or general queries"""
    prioritized_docs = prioritize_context_docs(query, context_docs)
    context_text = "\n\n".join([f"Document {i+1}:\n{doc}" for i, doc in enumerate(prioritized_docs)])
    
    history_text = ""
    if conversation_history and len(conversation_history) > 0:
        history_text = "## CONVERSATION HISTORY:\n" + "\n".join([
            f"User: {exchange['query']}\nAssistant: {summarize_response(exchange['response'])}" 
            for exchange in conversation_history[-3:]
        ]) + "\n\n"
    
    if is_product_query(query):
       prompt = f"""You are a helpful AI product assistant. Answer user queries about products based on the provided context.
If the answer isn't found in the context, politely say you don't know instead of making up information.

For product queries, output your response as a structured report with the following fields:
- Product Name: Name of the product
- Product Description: Brief description of the product
- Price: Price information (if available)
- URL: The URL to the product (if available, mark it with "[URL] " preceding the link)
- Picture: The picture of the product (if available, mark it with "[IMAGE] " preceding the image URL or description)
- Availability: Availability information (if available)
- Related Products: A list of related products (if any)
- Answer: Your complete natural language answer here

{history_text}## CONTEXT:
{context_text}

## CURRENT QUESTION:
{query}

## RESPONSE:
"""

    else:
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

    query_keywords = set(query.lower().split())
    scored_docs = [(sum(1 for kw in query_keywords if kw in doc.lower()), doc) for doc in context_docs]
    return [doc for _, doc in sorted(scored_docs, reverse=True)][:5]

def summarize_response(response: str, max_length=100) -> str:
    """Summarize a response to reduce token usage in history"""
    if response.strip().startswith('{') and response.strip().endswith('}'):
        try:
            response_data = json.loads(response)
            if "answer" in response_data:
                response = response_data["answer"]
        except Exception:
            pass
    return response if len(response) <= max_length else response[:max_length] + "..."

def is_product_query(query: str) -> bool:
    """Determine if a query is about products"""
    product_indicators = [
        "product", "buy", "purchase", "price", "cost", "how much", 
        "where can I get", "looking for", "search for", "find", 
        "show me", "available", "stock", "shipping", "delivery"
    ]
    return any(indicator in query.lower() for indicator in product_indicators)

def estimate_token_count(text: str) -> int:
    """Estimate the number of tokens in a text"""
    return len(text) // 4

def ask_llm(prompt: str) -> str:
    """Send a prompt to the Gemini API and get a response"""
    try:
        estimated_tokens = estimate_token_count(prompt)
        logger.info(f"Estimated prompt tokens: {estimated_tokens}")
        
        if estimated_tokens > 2000:
            logger.warning("Prompt too large, reducing context")
            prompt = reduce_prompt_size(prompt)
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 10240,
                "topP": 0.95,
                "topK": 10
            }
        }
        
        response = requests.post(
            GEMINI_API_URL, 
            headers={"Content-Type": "application/json"}, 
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            return response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        else:
            logger.error(f"API request failed with status {response.status_code}: {response.text}")
            return f"Error: Failed to get response from LLM (Status {response.status_code})"
    except Exception as e:
        logger.error(f"Error in LLM request: {e}")
        return f"Error: {str(e)}"

def reduce_prompt_size(prompt: str) -> str:
    """Reduce the size of the prompt to avoid token limits"""
    sections = {}
    current_section = "preamble"
    sections[current_section] = []
    
    for line in prompt.split('\n'):
        if line.startswith('## '):
            current_section = line[3:].strip()
            sections[current_section] = []
        else:
            sections.get(current_section, []).append(line)
    
    if "CONTEXT" in sections and len(sections["CONTEXT"]) > 20:
        context_lines = sections["CONTEXT"]
        doc_starts = [i for i, line in enumerate(context_lines) if line.startswith("Document ")]
        if len(doc_starts) > 3:
            sections["CONTEXT"] = context_lines[:doc_starts[3]]
    
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
    
    prompt_tokens = estimate_token_count(prompt)
    response_tokens = estimate_token_count(response)
    logger.info(f"Token usage - Prompt: {prompt_tokens}, Response: {response_tokens}, Total: {prompt_tokens + response_tokens}")
    
    return format_pretty_response(response)

def format_pretty_response(llm_response: str) -> str:
    """
    Format LLM response by:
    1. Removing status updates and wrappers
    2. Extracting the final product JSON
    3. Marking URLs and images with proper labels
    """
    # Handle streaming status updates pattern
    if llm_response.startswith('{"status":'):
        # Find the last JSON object (final response)
        parts = llm_response.split('{"status":')
        for part in reversed(parts):
            if part and '"answer":' in part:
                # Found the completion part with answer
                part = '{"status":' + part if not part.startswith('{') else part
                try:
                    json_part = json.loads(part)
                    if "answer" in json_part and json_part.get("status") == "complete":
                        llm_response = json_part["answer"]
                        break
                except:
                    continue
    
    # Now process the cleaned response
    try:
        # Try parsing as JSON
        product_data = json.loads(llm_response)
    except:
        # Not valid JSON, wrap in simple object
        return json.dumps({"answer": llm_response}, indent=4)
    
    # Remove any status keys
    if "status" in product_data:
        product_data.pop("status")
    
    # Mark URLs in fields
    if "url" in product_data and product_data["url"]:
        product_data["url"] = f"[URL] {product_data['url']}"
    
    if "image" in product_data and product_data["image"]:
        product_data["image"] = f"[IMAGE] {product_data['image']}"
    
    # Find and mark URLs in answer text
    if "answer" in product_data and isinstance(product_data["answer"], str):
        product_data["answer"] = re.sub(r'(https?://\S+)', r'[URL] \1', product_data["answer"])
    
    # Find and mark URLs in any text fields (recursively if needed)
    def mark_urls_in_obj(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str) and "http" in value:
                    obj[key] = re.sub(r'(https?://\S+)', r'[URL] \1', value)
                elif isinstance(value, (dict, list)):
                    mark_urls_in_obj(value)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                if isinstance(item, str) and "http" in item:
                    obj[i] = re.sub(r'(https?://\S+)', r'[URL] \1', item)
                elif isinstance(item, (dict, list)):
                    mark_urls_in_obj(item)
    
    mark_urls_in_obj(product_data)
    
    # Return pretty JSON
    return json.dumps(product_data, indent=4)