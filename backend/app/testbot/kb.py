import os
import json
import numpy as np
import faiss
import logging
from pathlib import Path
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple, Optional, Any

from config import BASE_KB_DIR, SUPPORTED_EXTENSIONS
from data_loader import load_file

# Configure logging
logger = logging.getLogger(__name__)

# Load the embedding model
embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def get_kb_dir(chatbot_id: str) -> str:
    """Get the KB directory for a specific chatbot"""
    kb_dir = os.path.join(BASE_KB_DIR, chatbot_id)
    os.makedirs(kb_dir, exist_ok=True)
    return kb_dir

def get_file_index_path(chatbot_id: str, file_path: str) -> str:
    """Generate the path for the file-specific index"""
    kb_dir = get_kb_dir(chatbot_id)
    file_name = Path(file_path).stem
    return os.path.join(kb_dir, f"{file_name}_index.faiss")

def get_file_docs_path(chatbot_id: str, file_path: str) -> str:
    """Generate the path for the file-specific documents"""
    kb_dir = get_kb_dir(chatbot_id)
    file_name = Path(file_path).stem
    return os.path.join(kb_dir, f"{file_name}_docs.json")

def file_index_exists(chatbot_id: str, file_path: str) -> bool:
    """Check if index for specific file exists"""
    index_path = get_file_index_path(chatbot_id, file_path)
    docs_path = get_file_docs_path(chatbot_id, file_path)
    return os.path.exists(index_path) and os.path.exists(docs_path)

def should_update_index(chatbot_id: str, file_path: str) -> bool:
    """Check if the index should be updated based on file modification time"""
    if not file_index_exists(chatbot_id, file_path):
        return True
    
    file_mod_time = os.path.getmtime(file_path)
    index_path = get_file_index_path(chatbot_id, file_path)
    index_mod_time = os.path.getmtime(index_path) if os.path.exists(index_path) else 0
    
    return file_mod_time > index_mod_time

def build_file_index(chatbot_id: str, file_path: str) -> Tuple[Optional[Any], Optional[List[str]]]:
    """Build an index for a specific file"""
    try:
        documents = load_file(file_path)
        
        if not documents:
            logger.warning(f"No documents loaded from {file_path}")
            return None, None
        
        # Create embeddings
        logger.info(f"Creating embeddings for {len(documents)} documents from {file_path}")
        embeddings = embedding_model.encode(documents)
        embeddings = np.array(embeddings).astype("float32")
        d = embeddings.shape[1]
        
        # Create FAISS index
        index = faiss.IndexFlatL2(d)
        index.add(embeddings)
        
        # Save index and documents
        index_path = get_file_index_path(chatbot_id, file_path)
        docs_path = get_file_docs_path(chatbot_id, file_path)
        
        faiss.write_index(index, index_path)
        with open(docs_path, "w") as f:
            json.dump(documents, f)
        
        logger.info(f"Built index for {file_path} with {len(documents)} documents")
        return index, documents
    
    except Exception as e:
        logger.error(f"Error building index for {file_path}: {e}")
        return None, None

def load_file_index(chatbot_id: str, file_path: str) -> Tuple[Optional[Any], Optional[List[str]]]:
    """Load index and documents for a specific file"""
    index_path = get_file_index_path(chatbot_id, file_path)
    docs_path = get_file_docs_path(chatbot_id, file_path)
    
    if not os.path.exists(index_path) or not os.path.exists(docs_path):
        return None, None
    
    try:
        index = faiss.read_index(index_path)
        with open(docs_path, "r") as f:
            documents = json.load(f)
        return index, documents
    except Exception as e:
        logger.error(f"Error loading index for {file_path}: {e}")
        return None, None

def discover_and_index_files(chatbot_id: str, data_dir: str) -> Dict[str, Tuple[Any, List[str]]]:
    """
    Discover all supported files in the data directory and build indexes for each
    Returns a dictionary of {file_path: (index, documents)}
    """
    indexes = {}
    
    # Make sure the directory exists
    if not os.path.exists(data_dir):
        logger.warning(f"Data directory {data_dir} does not exist")
        return indexes
    
    # Walk through the directory and find all supported files
    for root, _, files in os.walk(data_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if any(file.endswith(ext) for ext in SUPPORTED_EXTENSIONS):
                if should_update_index(chatbot_id, file_path):
                    logger.info(f"Building/updating index for {file_path}")
                    index, documents = build_file_index(chatbot_id, file_path)
                else:
                    logger.info(f"Loading existing index for {file_path}")
                    index, documents = load_file_index(chatbot_id, file_path)
                
                if index is not None and documents is not None:
                    indexes[file_path] = (index, documents)
    
    logger.info(f"Discovered and indexed {len(indexes)} files for {chatbot_id}")
    return indexes

def search_kb(chatbot_id: str, query: str, k: int = 5) -> List[str]:
    """
    Search across all file indexes for a chatbot and return the top results
    """
    # Use the existing chatbot_data directory structure
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                           "chatbot_data", chatbot_id)
    
    # Get all indexes for this chatbot
    indexes = discover_and_index_files(chatbot_id, data_dir)
    
    if not indexes:
        logger.warning(f"No indexes found for {chatbot_id}")
        return []
    
    # Encode the query
    query_embedding = embedding_model.encode([query])
    query_embedding = np.array(query_embedding).astype("float32")
    
    # Search each index and collect results
    all_results = []
    
    for file_path, (index, documents) in indexes.items():
        try:
            distances, indices = index.search(query_embedding, min(k, len(documents)))
            file_results = [(documents[idx], dist) for idx, dist in zip(indices[0], distances[0])]
            all_results.extend(file_results)
        except Exception as e:
            logger.error(f"Error searching index for {file_path}: {e}")
    
    # Sort by distance (lower is better) and get top-k
    all_results.sort(key=lambda x: x[1])
    top_results = [doc for doc, _ in all_results[:k]]
    
    return top_results