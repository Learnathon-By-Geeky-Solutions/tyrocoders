"""
Knowledge Base Indexing and Search Module

This module provides functionality for creating, managing, and searching vector-based knowledge bases
for chatbots using FAISS (Facebook AI Similarity Search) and sentence transformers. The system indexes
document chunks from various file types and enables semantic similarity searches against these indexes.

The module implements:
- File discovery and automated indexing for supported file types
- Vector embeddings generation using Sentence Transformers
- Efficient similarity search using FAISS indices
- Document-to-vector mapping with persistence
- Index management with update detection based on file modification times

Key Components:
1. Index Management: Creation, storage, and loading of FAISS indices for document chunks
2. Document Management: Storage and retrieval of document chunks corresponding to vectors
3. Search Functionality: Query embedding and multi-index search capabilities
4. File Discovery: Automatic detection and indexing of supported files

Dependencies:
    - sentence-transformers: For generating document and query embeddings
    - faiss: For efficient similarity search
    - numpy: For vector operations
    - json: For document storage and retrieval
    - os, pathlib: For file system operations
    - logging: For tracking indexing and search operations
    - config: For configuration settings (BASE_KB_DIR, SUPPORTED_EXTENSIONS)
    - data_loader: For loading and chunking documents from files

Architecture:
    - Each file has its own FAISS index (.faiss) and document store (.json)
    - Indices are organized by chatbot ID in a base knowledge base directory
    - Files are automatically re-indexed when modified

Functions:
    Directory and Path Management:
        get_kb_dir(chatbot_id): Get the knowledge base directory for a chatbot
        get_file_index_path(chatbot_id, file_path): Get the path for a file's FAISS index
        get_file_docs_path(chatbot_id, file_path): Get the path for a file's document store
    
    Index Status and Management:
        file_index_exists(chatbot_id, file_path): Check if an index exists for a file
        should_update_index(chatbot_id, file_path): Check if a file's index needs updating
    
    Index Building and Loading:
        build_file_index(chatbot_id, file_path): Build a new index for a file
        load_file_index(chatbot_id, file_path): Load an existing index for a file
        handle_file_indexing(chatbot_id, file_path): Handle index building or loading based on status
    
    File Discovery and Processing:
        discover_and_index_files(chatbot_id, data_dir): Discover and index all supported files
        is_supported_file(file): Check if a file has a supported extension
    
    Search:
        search_kb(chatbot_id, query, k): Search across all indexes for a chatbot

Usage Example:
    ```python
    # Search a chatbot's knowledge base
    results = search_kb(
        chatbot_id="support_bot",
        query="How do I reset my password?",
        k=3
    )
    
    # Display the top results
    for result in results:
        print(result)
    ```

Note:
    This module expects a specific directory structure where each chatbot has its own
    data directory containing the files to be indexed. The module automatically handles
    index creation, updates, and searches across all indexed files.
"""
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
    """
    Get the knowledge base directory for a specific chatbot.
    
    Creates the directory if it doesn't exist.
    
    Args:
        chatbot_id (str): Unique identifier for the chatbot
        
    Returns:
        str: Path to the chatbot's knowledge base directory
    """
    kb_dir = os.path.join(BASE_KB_DIR, chatbot_id)
    os.makedirs(kb_dir, exist_ok=True)
    return kb_dir

def get_file_index_path(chatbot_id: str, file_path: str) -> str:
    """
    Generate the path for the file-specific FAISS index.
    
    Args:
        chatbot_id (str): Unique identifier for the chatbot
        file_path (str): Path to the source file
        
    Returns:
        str: Path where the FAISS index for this file should be stored
    """
    kb_dir = get_kb_dir(chatbot_id)
    file_name = Path(file_path).stem
    return os.path.join(kb_dir, f"{file_name}_index.faiss")

def get_file_docs_path(chatbot_id: str, file_path: str) -> str:
    """
    Generate the path for the file-specific document store.
    
    Args:
        chatbot_id (str): Unique identifier for the chatbot
        file_path (str): Path to the source file
        
    Returns:
        str: Path where the JSON document store for this file should be stored
    """
    kb_dir = get_kb_dir(chatbot_id)
    file_name = Path(file_path).stem
    return os.path.join(kb_dir, f"{file_name}_docs.json")

def file_index_exists(chatbot_id: str, file_path: str) -> bool:
    """
    Check if index for specific file exists.
    
    Verifies that both the FAISS index and document store exist.
    
    Args:
        chatbot_id (str): Unique identifier for the chatbot
        file_path (str): Path to the source file
        
    Returns:
        bool: True if both index and document store exist, False otherwise
    """
    index_path = get_file_index_path(chatbot_id, file_path)
    docs_path = get_file_docs_path(chatbot_id, file_path)
    return os.path.exists(index_path) and os.path.exists(docs_path)

def should_update_index(chatbot_id: str, file_path: str) -> bool:
    """
    Check if the index should be updated based on file modification time.
    
    Compares the modification time of the source file against its index.
    If the file is newer than the index, the index should be updated.
    
    Args:
        chatbot_id (str): Unique identifier for the chatbot
        file_path (str): Path to the source file
        
    Returns:
        bool: True if the index needs to be updated, False otherwise
    """
    if not file_index_exists(chatbot_id, file_path):
        return True
    
    file_mod_time = os.path.getmtime(file_path)
    index_path = get_file_index_path(chatbot_id, file_path)
    index_mod_time = os.path.getmtime(index_path) if os.path.exists(index_path) else 0
    
    return file_mod_time > index_mod_time

def build_file_index(chatbot_id: str, file_path: str) -> Tuple[Optional[Any], Optional[List[str]]]:
    """
    Build an index for a specific file.
    
    Loads document chunks from the file, creates embeddings using the sentence transformer model,
    builds a FAISS index from these embeddings, and saves both the index and documents to disk.
    
    Args:
        chatbot_id (str): Unique identifier for the chatbot
        file_path (str): Path to the source file
        
    Returns:
        Tuple[Optional[Any], Optional[List[str]]]: 
            A tuple containing (FAISS index, list of document chunks), or (None, None) on failure
    
    Notes:
        - Uses the load_file function to extract document chunks from the file
        - Creates embeddings using the SentenceTransformer model
        - Uses a FlatL2 FAISS index for exact L2 distance search
    """
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
    """
    Load index and documents for a specific file.
    
    Loads the FAISS index and corresponding document store from disk.
    
    Args:
        chatbot_id (str): Unique identifier for the chatbot
        file_path (str): Path to the source file
        
    Returns:
        Tuple[Optional[Any], Optional[List[str]]]: 
            A tuple containing (FAISS index, list of document chunks), or (None, None) on failure
    """
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
    Discover all supported files in the data directory and build indexes for each.
    
    Walks through the data directory, identifies supported files, and builds or loads
    indexes for each file. Returns a dictionary mapping file paths to their indexes
    and document lists.
    
    Args:
        chatbot_id (str): Unique identifier for the chatbot
        data_dir (str): Directory containing files to be indexed
        
    Returns:
        Dict[str, Tuple[Any, List[str]]]: Dictionary mapping file paths to (index, documents) tuples
    
    Notes:
        - Only files with extensions in SUPPORTED_EXTENSIONS are processed
        - Indexes are built or updated as needed based on file modification times
    """
    indexes = {}

    if not os.path.exists(data_dir):
        logger.warning(f"Data directory {data_dir} does not exist")
        return indexes

    for root, _, files in os.walk(data_dir):
        for file in files:
            file_path = os.path.join(root, file)

            if not is_supported_file(file):
                continue

            index, documents = handle_file_indexing(chatbot_id, file_path)
            if index is not None and documents is not None:
                indexes[file_path] = (index, documents)

    logger.info(f"Discovered and indexed {len(indexes)} files for {chatbot_id}")
    return indexes

def is_supported_file(file: str) -> bool:
    """
    Check if a file has a supported extension.
    
    Args:
        file (str): Filename to check
        
    Returns:
        bool: True if the file has a supported extension, False otherwise
    
    Note:
        Supported extensions are defined in the SUPPORTED_EXTENSIONS configuration
    """
    return any(file.endswith(ext) for ext in SUPPORTED_EXTENSIONS)

def handle_file_indexing(chatbot_id: str, file_path: str) -> Tuple[Any, List[str]]:
    """
    Handle index building or loading based on file status.
    
    Checks if the index needs updating and either builds a new one or loads
    the existing one.
    
    Args:
        chatbot_id (str): Unique identifier for the chatbot
        file_path (str): Path to the source file
        
    Returns:
        Tuple[Any, List[str]]: A tuple containing (FAISS index, list of document chunks)
    """
    if should_update_index(chatbot_id, file_path):
        logger.info(f"Building/updating index for {file_path}")
        return build_file_index(chatbot_id, file_path)
    else:
        logger.info(f"Loading existing index for {file_path}")
        return load_file_index(chatbot_id, file_path)

def search_kb(chatbot_id: str, query: str, k: int = 5) -> List[str]:
    """
    Search across all file indexes for a chatbot and return the top results.
    
    Discovers all indexed files for the chatbot, searches each index for the query,
    and aggregates results to return the top-k most relevant document chunks.
    
    Args:
        chatbot_id (str): Unique identifier for the chatbot
        query (str): Search query text
        k (int, optional): Number of results to return. Defaults to 5.
        
    Returns:
        List[str]: List of document chunks most relevant to the query
    
    Process:
        1. Discovers and loads all indexes for the chatbot
        2. Encodes the query using the same embedding model used for indexing
        3. Searches each index and collects results with distances
        4. Sorts all results by distance (lower is better)
        5. Returns the top-k results across all indexes
    
    Notes:
        - Results are sorted by L2 distance (lower values indicate higher similarity)
        - If fewer than k results are available, returns all available results
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