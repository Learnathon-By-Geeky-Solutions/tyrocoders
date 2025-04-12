import os
import json
import requests
import logging
import re
from typing import Dict, Any, List, Optional
from config import GROQ_API_KEY, GEMINI_API_URL

from config import FREE_LLM_API_URL, FREE_LLM_API_KEY


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
        prompt = f"""You are a helpful AI product assistant. Answer user queries about products based only on the provided context. If the answer is not found in the context, reply with "I don't know" (inside the JSON response) without fabricating details.

    When answering a product query, examine the context for product details. If product details are available, return your answer as a JSON object with the following structure:
    {{
    "status": "success",
    "response": "Your complete natural language answer here",
    "product_data": {{
        "product_name": "Name of the product (or null if not available)",
        "product_description": "Brief description (or null)",
        "price": "Price information (or null)",
        "url": "The URL to the product (or null)",
        "picture": "The picture URL (or null)",
        "availability": "Availability information (or null)",
        "related_products": ["Product 1", "Product 2", "Product 3"]   // Use an empty list if no related products
    }}
    }}

    {history_text}
    ## CONTEXT:
    {context_text}

    ## CURRENT QUESTION:
    {query}

    ## RESPONSE:
    """
    else:
        prompt = f"""Answer the question concisely based on the provided context. If you don't find the answer in the context, reply with "I don't know". 
    Return your answer as a JSON object with these properties:
    {{
    "status": "success",
    "answer": "Your answer here"
    }}

    Only output the JSON object and nothing else.

    {history_text}
    ## CONTEXT:
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

    # Ensure query is a string
    if not isinstance(query, str):
        logger.warning(f"Query is not a string: {type(query)}")
        return context_docs[:5] if len(context_docs) > 5 else context_docs
        
    query_keywords = set(query.lower().split())
    
    # Handle different context document types safely
    scored_docs = []
    for doc in context_docs:
        # Check if doc is a string; if not, convert to string or handle appropriately
        if not isinstance(doc, str):
            try:
                doc_str = str(doc)
                logger.warning(f"Converting non-string document to string: {type(doc)}")
            except Exception as e:
                logger.error(f"Could not convert document to string: {e}")
                doc_str = ""
        else:
            doc_str = doc
            
        # Calculate score based on keyword matches
        score = sum(1 for kw in query_keywords if kw in doc_str.lower())
        scored_docs.append((score, doc))
    
    # Sort using only the score
    return [doc for _, doc in sorted(scored_docs, key=lambda x: x[0], reverse=True)][:5]


def summarize_response(response: str, max_length=100) -> str:
    """Summarize a response to reduce token usage in history"""
    if response.strip().startswith('{') and response.strip().endswith('}'):
        try:
            response_data = json.loads(response)
            if "answer" in response_data:
                response = response_data["answer"]
            elif "response" in response_data:
                response = response_data["response"]
        except Exception:
            pass
    return response if len(response) <= max_length else response[:max_length] + "..."

def is_product_query(query: str) -> bool:
    """
    Determine if a query is about products using a Hugging Face model
    """
    try:
        # Create a prompt for the model to classify the query
        prompt = f"""
        Task: Determine if the following query is related to shopping, products, purchases, or e-commerce.
        
        Query: "{query}"
        
        Is this a product-related query? Please analyze the query and respond with only "Yes" if it's related to products, shopping, or purchasing, or "No" if it's not.
        """
        
        # Use Hugging Face model to analyze the query
        headers = {
            "Authorization": f"Bearer {FREE_LLM_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": 100,  # Short response is fine for Yes/No
                "temperature": 0.95,  # Low temperature for more deterministic response
                "top_p": 0.9
            }
        }
        
        response = requests.post(
            FREE_LLM_API_URL,
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            logger.error(f"Error querying Hugging Face API: {response.status_code} - {response.text}")
            # Fall back to keyword-based detection as a backup
            return fallback_product_detection(query)
            
        response_text = response.json()[0]["generated_text"].strip().lower()
        
        # Check if the response contains "yes"
        is_product = "yes" in response_text.lower()
        
        logger.info(f"Query classified as product query: {is_product}")
        return is_product
        
    except Exception as e:
        logger.error(f"Error determining if query is product-related: {e}")
        # Fall back to keyword-based detection
        return fallback_product_detection(query)

def fallback_product_detection(query: str) -> bool:
    """Fallback method using keyword matching if the API call fails"""
    query = query.lower()
    product_indicators = [
        "product", "buy", "purchase", "price", "cost", "how much", 
        "where can i get", "looking for", "search for", "find", 
        "show me", "available", "stock", "shipping", "delivery",
        "shop", "discount", "deal", "offer", "sale", "coupon"
    ]
    return any(indicator in query.lower() for indicator in product_indicators)

def estimate_token_count(text: str) -> int:
    """Estimate the number of tokens in a text"""
    return len(text) // 4

def ask_groq(prompt: str, model="llama3-70b-8192") -> str:
    """Send a prompt to the Groq API and get a response"""
    try:
        estimated_tokens = estimate_token_count(prompt)
        logger.info(f"Estimated prompt tokens: {estimated_tokens}")
        
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "model": model,
            "temperature": 0.2,
            "max_tokens": 10240,
            "top_p": 0.95
        }
        
        logger.info(f"Sending request to Groq API with model: {model}")
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            logger.error(f"Groq API request failed with status {response.status_code}: {response.text}")
            # Fallback to Gemini if Groq fails
            logger.info("Falling back to Gemini API")
            return ask_llm_gemini(prompt)
        
        response_data = response.json()
        return response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
    
    except Exception as e:
        logger.error(f"Error in Groq request: {e}")
        # Fallback to Gemini
        logger.info(f"Falling back to Gemini API due to error: {e}")
        return ask_llm_gemini(prompt)

def ask_llm_gemini(prompt: str) -> str:
    """Send a prompt to the Gemini API and get a response (fallback)"""
    try:
        logger.info("Using Gemini API for response generation")
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
            logger.error(f"Gemini API request failed with status {response.status_code}: {response.text}")
            return f"Error: Failed to get response from LLM (Status {response.status_code})"
    except Exception as e:
        logger.error(f"Error in Gemini LLM request: {e}")
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

def process_query_llm(chatbot_id: str, query: str, context_docs: list, conversation_history=None) -> str:
    """Process a query using the appropriate context and LLM"""
    prompt = create_prompt(query, context_docs, conversation_history)
    logger.info(f"Sending prompt to Groq LLM for chatbot {chatbot_id}")
    
    # Try to estimate if the prompt is too large
    estimated_tokens = estimate_token_count(prompt)
    if estimated_tokens > 7000:  # Conservative limit for llama3-70b-8192
        logger.warning("Prompt too large, reducing context")
        prompt = reduce_prompt_size(prompt)
    
    # Use Groq as the primary LLM provider now
    response = ask_groq(prompt)
    
    prompt_tokens = estimate_token_count(prompt)
    response_tokens = estimate_token_count(response)
    logger.info(f"Token usage - Prompt: {prompt_tokens}, Response: {response_tokens}, Total: {prompt_tokens + response_tokens}")
    
    return response