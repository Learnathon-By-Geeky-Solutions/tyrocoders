import os
from kb import get_or_create_kb
from server import run_server

def knowledge_base_exists(chatbot_id):
    """
    Check if the KB already exists.
    For example, check if the FAISS index file is present.
    """
    index_path = os.path.join("kb_indexes", f"{chatbot_id}_index.faiss")
    return os.path.exists(index_path)

def main():
    # Compute the base directory (i.e. testbot directory)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "chatbot_data")
    
    # Build KB for Chatbot A
    chatbot_A_id = "chatbot_A"
    dir_chatbot_A = os.path.join(data_dir, "chatbot_A")
    data_paths_A = [
        os.path.join(dir_chatbot_A, "products.md"),
        os.path.join(dir_chatbot_A, "products.csv")
    ]
    if not knowledge_base_exists(chatbot_A_id):
        print(f"Building knowledge base for {chatbot_A_id}...")
        get_or_create_kb(chatbot_A_id, data_paths_A)
    else:
        print(f"Knowledge base for {chatbot_A_id} already exists.")
    
    # Build KB for Chatbot B
    chatbot_B_id = "chatbot_B"
    dir_chatbot_B = os.path.join(data_dir, "chatbot_B")
    data_paths_B = [
        os.path.join(dir_chatbot_B, "products.xlsx")
    ]
    if not knowledge_base_exists(chatbot_B_id):
        print(f"Building knowledge base for {chatbot_B_id}...")
        get_or_create_kb(chatbot_B_id, data_paths_B)
    else:
        print(f"Knowledge base for {chatbot_B_id} already exists.")
    
    # Continue with the rest of your chatbot initialization (e.g., starting the WebSocket server)
    run_server()

if __name__ == "__main__":
    main()
