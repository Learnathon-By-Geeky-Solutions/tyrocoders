import json
import asyncio
import logging
import websockets
from typing import Dict, Any

from kb import search_kb
from llm import process_query

# Configure logging
logger = logging.getLogger(__name__)

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
                # await websocket.send(json.dumps({"status": "searching", "message": "Searching knowledge base..."}))
                
                # Retrieve context from knowledge base
                context_docs = search_kb(chatbot_id, query, k=100)
                
                # Update client on progress
                # await websocket.send(json.dumps({"status": "thinking", "message": "Processing your query..."}))
                
                # Process query with LLM
                response_text = process_query(chatbot_id, query, context_docs)
                
                # Send final response
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