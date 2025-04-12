import json
import asyncio
import logging
import websockets
from typing import Dict, Any
import os

# Import the necessary modules directly
from kb import search_kb
from llm import  create_prompt, ask_groq, process_query_llm
from free_llm_formatter import format_response

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
    

async def process_query(client_id: str, chatbot_id: str, query: str) -> Dict[str, Any]:
    """Process a query with dual LLM approach"""
    try:
        # Search the knowledge base
        logger.info(f"Searching KB for chatbot {chatbot_id}, query: {query}")
        context_docs = search_kb(chatbot_id, query, 1000)
        
        # Get conversation history for this client
        client_history = conversation_history.get(client_id, [])
        
        # Create prompt
        prompt = create_prompt(query, context_docs, client_history)
        
        # Get raw response from primary LLM
        raw_response = process_query_llm(client_id, chatbot_id, context_docs, client_history)

        json_response = parse_and_clean_json_generic(raw_response)
        
        logger.info(f"The json_response  is : {json_response}")
        
        # Check if response is JSON (for product queries)
        is_json_response = False
        product_data = None
        
        
        # Format the text response using the free LLM
        
        # Update conversation history with the formatted response
        client_history.append({"query": query, "response": raw_response})
        # Keep only last 5 exchanges to manage context size
        conversation_history[client_id] = client_history[-5:] if len(client_history) > 5 else client_history
        
        # Return the appropriate response format
        if is_json_response and product_data:
            return  json_response       
        else:
            return json_response
    
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return {
            "status": "error",
            "message": f"Error processing query: {str(e)}"
        }

async def handle_client(websocket):
    """Handle client connection and messages"""
    client_id = str(id(websocket))
    logger.info(f"Client {client_id} connected")
    
    try:
        async for message in websocket:
            try:
                # Parse the incoming message
                data = json.loads(message)
                logger.info(f"Received message from client {client_id}: {data}")
                
                # Extract required fields
                chatbot_id = data.get("chatbot_id")
                query = data.get("query")
                
                # Validate input
                if not chatbot_id or not query:
                    error_msg = {"status": "error", "message": "Missing required fields: chatbot_id and query"}
                    await websocket.send(json.dumps(error_msg))
                    continue
                
                # Update client on progress
                await websocket.send(json.dumps({"status": "searching", "message": "Searching knowledge base..."}))
                
                # Process query with dual LLM approach
                response = await process_query(client_id, chatbot_id, query)
                
                # Send response to client
                await websocket.send(json.dumps(response))
                
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON from client {client_id}")
                await websocket.send(json.dumps({"status": "error", "message": "Invalid JSON format"}))
            except Exception as e:
                logger.error(f"Error processing message from client {client_id}: {e}")
                await websocket.send(json.dumps({"status": "error", "message": f"Server error: {str(e)}"}))
    
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"Client {client_id} disconnected")
    except Exception as e:
        logger.error(f"Unexpected error with client {client_id}: {e}")

async def start_server(host="0.0.0.0", port=8090):
    """Start the WebSocket server"""
    server = await websockets.serve(handle_client, host, port)
    logger.info(f"WebSocket server running on {host}:{port}")
    
    # Keep the server running
    await server.wait_closed()

def run_server(host="0.0.0.0", port=8090):
    """Run the WebSocket server"""
    logger.info("Starting WebSocket server with dual LLM processing...")
    asyncio.run(start_server(host, port))

if __name__ == "__main__":
    run_server()