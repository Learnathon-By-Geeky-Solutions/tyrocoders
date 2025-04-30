"""
server.py

This module defines the WebSocket server responsible for handling real-time communication
between clients and the chatbot service.

Core Responsibilities:
- Accepts WebSocket connections from clients.
- Receives and parses messages that include a chatbot ID and user query.
- Validates the incoming request.
- Searches the chatbot's knowledge base using the provided query.
- Generates a response using a connected large language model (LLM).
- Sends the response and metadata (e.g., number of sources used) back to the client.

Functions:
- handle_client(websocket): Handles the message lifecycle for each client connection.
- start_server(host, port): Initializes and starts the WebSocket server using asyncio.
- run_server(host, port): Entry point to run the WebSocket server.
"""

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
    """
    Handle communication with a connected WebSocket client.

    Parameters:
        websocket (websockets.WebSocketServerProtocol): The WebSocket connection to the client.

    This function:
    - Receives JSON-formatted messages from the client.
    - Validates that required fields ('chatbot_id' and 'query') are present.
    - Uses the chatbot ID to retrieve relevant documents from the knowledge base.
    - Sends a response back to the client using LLM-generated text based on retrieved context.
    - Catches and logs JSON decoding and processing errors.
    """
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
                
                # Retrieve context from knowledge base
                context_docs = search_kb(chatbot_id, query, k=100)
                
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
    """
    Start the WebSocket server using asyncio and bind to a host and port.

    Parameters:
        host (str): Host IP address to bind the server to (default is "0.0.0.0").
        port (int): Port number to bind the server to (default is 8090).

    The server runs indefinitely, handling connections with `handle_client`.
    """
    server = await websockets.serve(handle_client, host, port)
    logger.info(f"WebSocket server running on {host}:{port}")
    await server.wait_closed()

def run_server(host="0.0.0.0", port=8090):
    """
    Entry point to start the WebSocket server.

    Parameters:
        host (str): Host IP address to bind the server to.
        port (int): Port number to listen on.

    This function wraps `start_server` with `asyncio.run`.
    """
    logger.info("Starting WebSocket server...")
    asyncio.run(start_server(host, port))
