import json
import asyncio
import logging
import websockets
from typing import Dict, Any, List
from collections import defaultdict

from kb import search_kb
from llm import process_query

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Store conversation history for each client
conversation_history = defaultdict(list)
# Store the last product mentioned for each client
last_product_context = {}

async def handle_client(websocket):
    """Handle client connection and messages"""
    client_id = id(websocket)
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
                
                # Check if query is related to previous product context
                current_product = extract_product_from_query(query)
                prev_product = last_product_context.get(client_id)
                
                # Determine search strategy based on conversation context
                if is_followup_question(query) and prev_product and not current_product:
                    # This is a follow-up about the previous product
                    logger.info(f"Follow-up question about {prev_product}")
                    # Use the previous product name to enhance the search
                    enhanced_query = f"{prev_product} {query}"
                    context_docs = search_kb(chatbot_id, enhanced_query, k=1000)
                else:
                    # New product query or general question
                    context_docs = search_kb(chatbot_id, query, k=1000)
                    if current_product:
                        last_product_context[client_id] = current_product
                
                # Update client on progress
                await websocket.send(json.dumps({"status": "thinking", "message": "Processing your query..."}))
                
                # Get conversation history for this client
                client_history = conversation_history[client_id][-5:] if client_id in conversation_history else []
                
                # Process query with LLM
                response_text = process_query(chatbot_id, query, context_docs, client_history)
                
                # Store the interaction in conversation history
                conversation_history[client_id].append({
                    "query": query,
                    "response": response_text
                })
                
                # Limit conversation history size
                if len(conversation_history[client_id]) > 10:
                    conversation_history[client_id] = conversation_history[client_id][-10:]
                
                # Try to extract structured data if it's a product response
                try:
                    # Check if response is JSON formatted
                    if response_text.strip().startswith('{') and response_text.strip().endswith('}'):
                        response_data = json.loads(response_text)
                        
                        # Send structured response
                        await websocket.send(json.dumps({
                            "status": "complete",
                            "structured_data": response_data,
                            "answer": response_data.get("answer", response_text),
                            "sources": len(context_docs)
                        }))
                    else:
                        # Send regular text response
                        await websocket.send(json.dumps({
                            "status": "complete",
                            "answer": response_text,
                            "sources": len(context_docs)
                        }))
                except json.JSONDecodeError:
                    # If response isn't valid JSON, send as plain text
                    await websocket.send(json.dumps({
                        "status": "complete",
                        "answer": response_text,
                        "sources": len(context_docs)
                    }))
                
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

def extract_product_from_query(query: str) -> str:
    """Extract potential product names from a query
    This is a simplified version - in production, consider using NER models"""
    # Simple keyword detection - in real implementation use NLP
    product_indicators = ["show me", "looking for", "find", "search for", "information about"]
    query_lower = query.lower()
    
    for indicator in product_indicators:
        if indicator in query_lower:
            # Extract text after the indicator
            product_part = query_lower.split(indicator, 1)[1].strip()
            # Take the first few words as the potential product
            words = product_part.split()
            if len(words) > 2:
                return " ".join(words[:3])
            return product_part
    
    return ""

def is_followup_question(query: str) -> bool:
    """Determine if a query is likely a follow-up question"""
    followup_indicators = [
        "how much", "what about", "is it", "does it", "can it", 
        "tell me more", "more info", "price", "color", "size",
        "also", "too", "as well", "another", "different"
    ]
    
    query_lower = query.lower()
    # Check if query starts with a pronoun or lacks a subject
    if any(query_lower.startswith(word) for word in ["it", "that", "this", "they", "those"]):
        return True
        
    # Check for other follow-up indicators
    if any(indicator in query_lower for indicator in followup_indicators):
        return True
        
    return False

async def start_server(host="0.0.0.0", port=8090):
    """Start the WebSocket server"""
    server = await websockets.serve(handle_client, host, port)
    logger.info(f"WebSocket server running on {host}:{port}")
    
    # Keep the server running
    await server.wait_closed()

def run_server(host="0.0.0.0", port=8090):
    """Run the WebSocket server"""
    logger.info("Starting WebSocket server...")
    asyncio.run(start_server(host, port))

if __name__ == "__main__":
    run_server()