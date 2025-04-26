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
    """Discover all chatbot directories in the chatbot_data directory"""
    chatbots = []
    
    # Create data dir if it doesn't exist
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        logger.info(f"Created data directory: {DATA_DIR}")
        return chatbots
    
    # Find all subdirectories in the data directory (each is a chatbot)
    for item in os.listdir(DATA_DIR):
        item_path = os.path.join(DATA_DIR, item)
        if os.path.isdir(item_path):
            chatbots.append(item)
    
    return chatbots

def main():
    """Main entry point for the application"""
    logger.info(f"Starting chatbot service using data from {DATA_DIR}...")
    
    # Discover chatbots
    chatbots = discover_chatbots()
    logger.info(f"Discovered {len(chatbots)} chatbots: {', '.join(chatbots)}")
    
    # Index all chatbot knowledge bases
    for chatbot_id in chatbots:
        logger.info(f"Indexing knowledge base for {chatbot_id}...")
        chatbot_data_dir = os.path.join(DATA_DIR, chatbot_id)
        discover_and_index_files(chatbot_id, chatbot_data_dir)
    
    # Start the server
    logger.info("Starting WebSocket server...")
    run_server()

if __name__ == "__main__":
    main()