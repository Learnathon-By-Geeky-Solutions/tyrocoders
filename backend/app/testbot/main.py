"""
main.py

Entry point for the chatbot WebSocket server application.

This script performs the following tasks:
1. Configures logging for the application.
2. Discovers chatbot directories under the configured data directory.
3. Indexes the knowledge base for each discovered chatbot.
4. Starts the WebSocket server to handle client queries in real time.

Functions:
- discover_chatbots: Finds and returns chatbot IDs based on subdirectories in the data directory.
- main: Orchestrates the discovery, indexing, and server startup process.

To run the server:
    python main.py
"""

import os
import logging
from pathlib import Path
from server import run_server
from kb import discover_and_index_files
from config import DATA_DIR

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def discover_chatbots():
    """
    Discover all chatbot directories in the DATA_DIR directory.

    Each subdirectory inside DATA_DIR is considered a separate chatbot, and
    will have its own knowledge base.

    Returns:
        list: A list of chatbot IDs (subdirectory names).
    """
    chatbots = []
    
    # Create data directory if it doesn't exist
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        logger.info(f"Created data directory: {DATA_DIR}")
        return chatbots
    
    # Find all subdirectories (chatbot IDs)
    for item in os.listdir(DATA_DIR):
        item_path = os.path.join(DATA_DIR, item)
        if os.path.isdir(item_path):
            chatbots.append(item)
    
    return chatbots

def main():
    """
    Main entry point for the chatbot application.

    This function:
    - Logs startup status
    - Discovers all chatbot subdirectories
    - Indexes all knowledge base files for each chatbot
    - Starts the WebSocket server to serve client queries
    """
    logger.info(f"Starting chatbot service using data from {DATA_DIR}...")
    
    # Discover available chatbots
    chatbots = discover_chatbots()
    logger.info(f"Discovered {len(chatbots)} chatbots: {', '.join(chatbots)}")
    
    # Index all chatbot knowledge bases
    for chatbot_id in chatbots:
        logger.info(f"Indexing knowledge base for {chatbot_id}...")
        chatbot_data_dir = os.path.join(DATA_DIR, chatbot_id)
        discover_and_index_files(chatbot_id, chatbot_data_dir)
    
    # Start the WebSocket server
    logger.info("Starting WebSocket server...")
    run_server()

if __name__ == "__main__":
    main()
