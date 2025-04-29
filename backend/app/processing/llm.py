import json
import requests
from typing import Dict, Any, List, Optional
from core.config import GROQ_API_KEY, GEMINI_API_URL
from core.config import FREE_LLM_API_URL, FREE_LLM_API_KEY
from core.logger import logger


def create_prompt(query: str, context_docs: list, conversation_history=None) -> str:
    """Create prompt for the LLM based on product or general queries"""
    context_text = "\n\n".join([f"Document {i+1}:\n{doc}" for i, doc in enumerate(context_docs)])
    # context_text = ""
    history_text = conversation_history
    logger.info("starting point of create prompt")
    
    logger.info("Staring the product prompt")
    if is_product_query(query):
        logger.debug("inside the produce prompt ")
        prompt = f"""
        You are an AI shopping assistant for an ecommerce website. Your goal is to help users find products, answer questions about products, and provide a helpful shopping experience.

        ## Input Data
        You will receive:
        - `{history_text}`: Previous conversation history with the user
        - `{context_text}`: Product database information in JSON format
        - `{query}`: The user's current question or request

        ## Response Format
        Your responses must always be in the following JSON format:

        ```json
        {{
        "response": "Your conversational response to the user here",
        "display_type": "text|product_card|product_grid|comparison_table",
        "follow_up_question": "An optional follow-up question to engage the user",
        "products": [
            {{
            "row_index": 1,
            "url": "product-url-slug",
            "name": "Product Name",
            "price": "Price as string with currency symbol",
            "image": "URL to product image"
            }}
        ]
        }}
        ```

        ## Mandatory and Optional Fields

        ### Mandatory Fields for All Products:
        - `row_index`: Numeric position in the list (starting at 1)
        - `url`: The product URL slug
        - `name`: Product name
        - `price`: Product price with currency symbol
        - `image`: URL to product image

        ### Optional Fields (Add Only When Relevant):
        For detailed product views:
        - `description`: A short and concise summary of the product description
        - `key_features`: Array of important product features
        - `ratings`: Customer rating if available
        - `availability`: Stock status

        For comparison tables, include relevant comparison attributes like:
        - `processor`: For electronics comparisons
        - `material`: For clothing or furniture
        - `size_options`: For products with size variations
        - Any other attributes relevant to the specific product category being compared

        ## Guidelines

        1. **Display Types**:
        - `text`: For general responses with no product display needed
        - `product_card`: For displaying a single product in detail
        - `product_grid`: For displaying multiple products in a grid
        - `comparison_table`: For comparing multiple products side by side

        2. **Product Information**:
        - Always include the five mandatory fields for all products
        - Add optional fields only when they're relevant to the user's query
        - For comparison tables, include the specific attributes needed for comparison
        - Summarize product descriptions in clear, concise language
        - Correct any spelling or formatting issues from the original product data

        3. **User Interaction**:
        - Be conversational, friendly, and helpful
        - Include a follow-up question when appropriate to guide the user
        - If user query is vague, ask for clarification
        - If you can't find a product in the context, apologize and suggest alternatives

        4. **Search Understanding**:
        - Handle queries about product categories ("show me laptops")
        - Handle specific product searches ("tell me about the iPhone 13")
        - Handle feature-based searches ("waterproof cameras under $500")
        - Handle comparison requests ("compare Dell XPS vs MacBook Pro")

        5. **Special Cases**:
        - For product comparisons, set `display_type` to "comparison_table" and include relevant comparison attributes
        - For browsing multiple products, set `display_type` to "product_grid" with mandatory fields only
        - For detailed product information, set `display_type` to "product_card" with additional descriptive fields
        - For general questions or when no products match, set `display_type` to "text" and omit the products array

        Remember to always format your response as valid JSON with the structure shown above.
        """
    else:
        prompt = f"""
        You are an AI shopping assistant for an ecommerce website. Your goal is to help users primarily with shopping, but you can also handle casual conversation. For queries unrelated to products, respond appropriately based on the type of query.

        ## Input Data
        You will receive:
        - `{history_text}`: Previous conversation history with the user
        - `{query}`: The user's current question or request

        ## Response Format
        Your responses must always be in the following JSON format:

        ```json
        {{
        "response": "Your conversational response to the user here",
        "display_type": "text",
        "follow_up_question": "An optional follow-up question to engage the user",
        "conversation_type": "casual|support|irrelevant"
        }}
        ```

        ## Guidelines for Non-Product Queries

        1. **Casual Conversation** (set conversation_type to "casual"):
        - Handle greetings, thanks, and general chitchat politely and briefly
        - Be friendly and conversational, but concise
        - Include a follow-up question that gently steers the conversation back to shopping when appropriate
        - Examples: "Hello", "How are you?", "Thanks for your help", etc.

        2. **Support Questions** (set conversation_type to "support"):
        - For questions about orders, shipping, returns, account issues, technical problems
        - Politely apologize and direct the user to contact customer support 
        - Provide a helpful, empathetic response without attempting to solve complex support issues
        - Examples: "Where is my order?", "How do I return this item?", "I can't log into my account", etc.

        3. **Irrelevant Queries** (set conversation_type to "irrelevant"):
        - For completely off-topic questions or requests unrelated to shopping or the website
        - Politely explain that you're a shopping assistant and can't help with the specific request
        - Redirect the conversation to shopping-related topics
        - Examples: "Write me an essay", "What's the capital of France?", "Tell me a joke", etc.

        Remember to always format your response as valid JSON with the structure shown above, and use display_type "text" for all non-product queries.
        """
    
    return prompt

def prioritize_context_docs(query: str, context_docs: list) -> list:
    """Filter and prioritize context documents based on relevance to query"""
    if len(context_docs) <= 5:
        return context_docs

    if not isinstance(query, str):
        logger.warning(f"Query is not a string: {type(query)}")
        return context_docs[:5]
        
    query_keywords = set(query.lower().split())
    scored_docs = []
    for doc in context_docs:
        if not isinstance(doc, str):
            try:
                doc_str = str(doc)
                logger.warning(f"Converting non-string document to string: {type(doc)}")
            except Exception as e:
                logger.error(f"Could not convert document to string: {e}")
                doc_str = ""
        else:
            doc_str = doc
            
        score = sum(1 for kw in query_keywords if kw in doc_str.lower())
        scored_docs.append((score, doc))
    
    # For product queries, return more items. Otherwise limit to 5.
    if is_product_query(query):
        return [doc for _, doc in sorted(scored_docs, key=lambda x: x[0], reverse=True)][:10]
    else:
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

def is_product_query(query: str, history_text: str = "") -> bool:
    """
    Determine if a query is about products using a Hugging Face model.
    """
    try:
        prompt = f"""
        Task: Using the conversation context provided, determine if the new query is related to shopping, products, purchases, or e-commerce.

        Conversation History:
        {history_text}
        
        New Query: "{query}"
        
        Is this a product-related query? Please analyze the conversation history and the new query, and respond with only "Yes" if it's related to products, shopping, or purchasing, or "No" if it is not.
        """
        
        headers = {
            "Authorization": f"Bearer {FREE_LLM_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": 100,
                "temperature": 0.95,
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
            return fallback_product_detection(query)
            
        response_text = response.json()[0]["generated_text"].strip().lower()
        is_product = "yes" in response_text
        
        logger.info(f"Query classified as product query: {is_product}")
        return is_product
        
    except Exception as e:
        logger.error(f"Exception during product query detection: {e}")
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
        # estimated_tokens = estimate_token_count(prompt)
        # logger.info(f"Estimated prompt tokens: {estimated_tokens}")
        
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
            logger.info("Falling back to Gemini API")
            return ask_llm_gemini(prompt)
        
        response_data = response.json()
        return response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
    
    except Exception as e:
        logger.error(f"Error in Groq request: {e}")
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
    
    estimated_tokens = estimate_token_count(prompt)
    response = ask_llm_gemini(prompt)
    
    prompt_tokens = estimate_token_count(prompt)
    response_tokens = estimate_token_count(response)
    logger.info(f"Token usage - Prompt: {prompt_tokens}, Response: {response_tokens}, Total: {prompt_tokens + response_tokens}")
    
    return response