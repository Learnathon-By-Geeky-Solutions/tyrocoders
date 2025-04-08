# server.py
import json
import asyncio
import websockets
from kb import search_kb
from llm import ask_llm

async def process_query(websocket):
    """
    For each incoming message, process the query using the correct chatbot's KB.
    """
    try:
        async for message in websocket:
            print("Received message:", message)
            try:
                data = json.loads(message)
                chatbot_id = data.get("chatbot_id")
                query = data.get("query")
                if not chatbot_id or not query:
                    response_text = "Invalid message format. Expected keys: 'chatbot_id' and 'query'."
                else:
                    # Retrieve context from the KB
                    context_docs, _ = search_kb(chatbot_id, query, k=100)
                    context_text = "\n".join(context_docs)
                    prompt = (f"Use the following information to answer the question.\n\n"
                              f"Context:\n{context_text}\n\nQuestion: {query}\nAnswer:")
                    response_text = ask_llm(prompt)
            except json.JSONDecodeError:
                response_text = "Invalid JSON message received."
            # Send the answer and an end marker
            await websocket.send(response_text)
            await websocket.send("[END]")
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
    except Exception as e:
        print(f"Error in process_query: {e}")

async def start_server():
    port = 8090
    async with websockets.serve(process_query, "0.0.0.0", port):
        print(f"WebSocket server running on port {port}...")
        await asyncio.Future()  # run forever

def run_server():
    asyncio.run(start_server())
