import json
import asyncio
import logging
import websockets
from typing import Dict, Any
from agents.conversation_manager import ConversationManagerAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize conversation manager
conversation_manager = ConversationManagerAgent()

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
                
                # Process with multi-agent system
                try:
                    # Update client that we're analyzing the query
                    
                    
                    # Process with conversation manager
                    response = await conversation_manager.process_message(client_id, chatbot_id, query)
                    
                    # Send response to client
                    await websocket.send(json.dumps(response))
                    
                except Exception as e:
                    logger.error(f"Error in multi-agent processing: {e}")
                    await websocket.send(json.dumps({
                        "status": "error", 
                        "message": f"Error processing your request: {str(e)}"
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
    logger.info("Starting WebSocket server with multi-agent architecture...")
    asyncio.run(start_server(host, port))

if __name__ == "__main__":
    run_server()