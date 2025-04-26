import json
from typing import Dict, Any

from core.logger import logger
# Import the necessary modules directly
from processing.kb import search_kb
from processing.llm import create_prompt, ask_llm_gemini
from core.logger import logger
# Import the singleton Vanna instance from chatbot_service
from services.chatbot_service import vanna
# Store conversation history 
conversation_history = {}

def clean_json_response(response_data: dict) -> dict:
    """
    Cleans the provided JSON object by stripping leading and trailing whitespace
    from all string values.
    
    Args:
        response_data (dict): The input JSON object as a dictionary.
    
    Returns:
        dict: A new dictionary with cleaned string values.
    """
    cleaned_data = {}
    for key, value in response_data.items():
        if isinstance(value, str):
            cleaned_value = value.strip()
        elif isinstance(value, list):
            cleaned_value = [item.strip() if isinstance(item, str) else item for item in value]
        elif isinstance(value, dict):
            cleaned_value = clean_json_response(value)
        else:
            cleaned_value = value
        cleaned_data[key] = cleaned_value
    return cleaned_data

def parse_and_clean_json_generic(input_string: str) -> dict:
    """
    Removes any characters before the first '{' and after the last '}' in the input string,
    then parses the resulting JSON and cleans it.
    
    Args:
        input_string (str): The raw input string containing JSON.
    
    Returns:
        dict: The cleaned JSON object.
    
    Raises:
        ValueError: If no valid JSON object is found.
    """
    # Find the first occurrence of '{' and the last occurrence of '}'
    idx_start = input_string.find("{")
    idx_end = input_string.rfind("}")
    
    if idx_start == -1 or idx_end == -1 or idx_end < idx_start:
        raise ValueError("No valid JSON object found in the input string.")
    
    # Extract the substring that should form the JSON object
    json_string = input_string[idx_start: idx_end + 1]
    
    try:
        data = json.loads(json_string)
    except json.JSONDecodeError as e:
        raise ValueError("The extracted string is not valid JSON.") from e
    
    return clean_json_response(data)
    

async def process_query(user_id: str, chatbot_id: str, query: str, conversation_history=None) -> Dict[str, Any]:
    """Process a query with dual LLM approach"""
    try:
        # Search the knowledge base
        logger.info(f"Searching KB for chatbot {chatbot_id}, query: {query}")
        context_docs = search_kb(chatbot_id, query, 1000)
        # logger.info(f"context docs: {len(context_docs)}")
        
        # Use provided conversation history if available, otherwise use the global one
        client_history = conversation_history if conversation_history else conversation_history.get(user_id, [])
        # logger.debug(f"client history is defined {client_history}")
        # Create prompt
        prompt = create_prompt(query, context_docs, client_history)
        
        # logger.debug("Prompt is defined {prompt}")
        from processing.db_storage import DatabaseStorageManager

        # 1) Grab your Vanna instance
        vn = vanna.get_instance(chatbot_id)
        
        # 2) Make sure it’s pointing at the right SQLite DB
        storage_mgr = DatabaseStorageManager()
        config = storage_mgr.load_config(chatbot_id)
        vn.connect_to_sqlite(config["db_path"])
        
        
        # 3) Now ask Vanna using your raw query (and pass the contexts in if supported)
        # ——— simple “ask” by query alone ———
        answer = vn.ask(question=query)
        logger.info(answer)
        # Get raw response from primary LLM (Gemini as fallback is used inside ask_llm_gemini)
        raw_response = ask_llm_gemini(prompt)
        
        json_response = parse_and_clean_json_generic(raw_response)
        
        logger.info(f"The json_response is : {json_response}")
        
        # Check if the response contains product-specific keys
        is_json_response = False
        product_data = None
        if "row_index" in json_response and "target" in json_response:
            is_json_response = True
            product_data = json_response
        
        # Update conversation history if we're using the global one
        if not conversation_history:
            client_history.append({"query": query, "response": raw_response})
            # Keep only last 5 exchanges to manage context size
            conversation_history[user_id] = client_history[-5:] if len(client_history) > 5 else client_history
        
        # Return the appropriate response format
        if is_json_response and product_data:
            return product_data       
        else:
            return json_response
    
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return {
            "status": "error",
            "message": f"Error processing query: {str(e)}"
        }

async def handle_client(chatbot_id=None, user_message=None, conversation_history=None, 
                       conversation_id=None, user_id=None, ai_model_name = None):
    """Handle client connection and messages"""
    logger.info(f"User {user_id} connected with conversation_id {conversation_id}")
    
    try:
        # Validate input
        if not chatbot_id or not user_message:
            error_msg = "Missing required fields: chatbot_id and user_message"
            logger.error(error_msg)
            return False, None, error_msg
        
        # Process query with dual LLM approach
        response = await process_query(user_id, chatbot_id, user_message, conversation_history)
        
        # Check if response indicates an error
        if "status" in response and response["status"] == "error":
            return False, None, response.get("message", "Unknown error occurred")
        
        # Process successful response
        return True, response, None
    
    except json.JSONDecodeError:
        error_msg = f"Invalid JSON from user {user_id}"
        logger.error(error_msg)
        return False, None, error_msg
    except Exception as e:
        error_msg = f"Error processing message from user {user_id}: {e}"
        logger.error(error_msg)
        return False, None, f"Server error: {str(e)}"