import os
import json
import numpy as np
import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
import warnings
from functools import lru_cache

from core.config import SUPPORTED_EXTENSIONS
from core.logger import logger

# Suppress FAISS and numpy warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", module="faiss")

BASE_KB_DIR = "./kb_storage"

# Lazy-loaded resources
_EMBEDDING_MODEL = None
_FAISS_IMPORTED = False
FAISS_INDEX = "index.faiss"

def get_embedding_model():
    """Get the sentence transformer embedding model with lazy loading.
    
    Returns:
        SentenceTransformer: The loaded embedding model (all-MiniLM-L6-v2)
    """
    global _EMBEDDING_MODEL
    if _EMBEDDING_MODEL is None:
        from sentence_transformers import SentenceTransformer
        logger.info("Loading SentenceTransformer model...")
        _EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
    return _EMBEDDING_MODEL

@lru_cache(maxsize=32)
def get_kb_dir(chatbot_id: str) -> str:
    """Get or create knowledge base directory for a chatbot.
    
    Args:
        chatbot_id: Unique identifier for the chatbot
        
    Returns:
        str: Path to the knowledge base directory
    """
    kb_dir = os.path.join(BASE_KB_DIR, chatbot_id)
    os.makedirs(kb_dir, exist_ok=True)
    return kb_dir

def get_meta_data_path(chatbot_id: str) -> str:
    """Get path to metadata file for a chatbot's knowledge base.
    
    Args:
        chatbot_id: Unique identifier for the chatbot
        
    Returns:
        str: Path to the metadata.json file
    """
    return os.path.join(get_kb_dir(chatbot_id), "metadata.json")

def kb_exists(chatbot_id: str) -> bool:
    """Check if knowledge base exists for a chatbot.
    
    Args:
        chatbot_id: Unique identifier for the chatbot
        
    Returns:
        bool: True if both index and documents exist, False otherwise
    """
    index_path = os.path.join(get_kb_dir(chatbot_id), FAISS_INDEX)
    docs_path = os.path.join(get_kb_dir(chatbot_id), "documents.json")
    return os.path.exists(index_path) and os.path.exists(docs_path)

def get_indexed_files_metadata(chatbot_id: str) -> Dict:
    """Get metadata about indexed files for a chatbot.
    
    Args:
        chatbot_id: Unique identifier for the chatbot
        
    Returns:
        Dict: Dictionary containing metadata about indexed files
    """
    meta_path = get_meta_data_path(chatbot_id)
    if os.path.exists(meta_path):
        with open(meta_path, "r") as f:
            return json.load(f)
    return {}

def should_update_index(chatbot_id: str, file_paths: List[str]) -> bool:
    """Check if index needs updating based on file modifications.
    
    Args:
        chatbot_id: Unique identifier for the chatbot
        file_paths: List of file paths to check
        
    Returns:
        bool: True if index needs updating, False otherwise
    """
    if not kb_exists(chatbot_id):
        return True
    
    metadata = get_indexed_files_metadata(chatbot_id)
    indexed_files = metadata.get("indexed_files", {})
    
    # Check if files have changed
    if set(indexed_files.keys()) != set(file_paths):
        return True
    
    # Check modification times
    for file_path in file_paths:
        file_mod_time = os.path.getmtime(file_path)
        if file_path not in indexed_files or file_mod_time > indexed_files[file_path]:
            return True
    
    return False

def build_knowledge_base(chatbot_id: str, file_paths: List[str]) -> bool:
    """Build or update knowledge base from files.
    
    Args:
        chatbot_id: Unique identifier for the chatbot
        file_paths: List of file paths to include in knowledge base
        
    Returns:
        bool: True if knowledge base was built successfully, False otherwise
    """
    try:
        global _FAISS_IMPORTED
        if not _FAISS_IMPORTED:
            import faiss
            _FAISS_IMPORTED = True

        from processing.data_loader import load_file
        
        all_documents = []
        all_document_texts = []
        file_metadata = {}
        
        # Process each file
        for file_path in file_paths:
            if not os.path.exists(file_path):
                logger.warning(f"File {file_path} does not exist")
                continue
                
            if not any(file_path.endswith(ext) for ext in SUPPORTED_EXTENSIONS):
                logger.warning(f"Unsupported file type: {file_path}")
                continue
            
            documents = load_file(file_path)
            if not documents:
                logger.warning(f"No documents loaded from {file_path}")
                continue
            
            document_texts = get_text_chunks(documents)
            all_documents.extend(documents)
            all_document_texts.extend(document_texts)
            file_metadata[file_path] = os.path.getmtime(file_path)
        
        if not all_documents:
            logger.warning(f"No documents loaded for {chatbot_id}")
            return False
        
        # Create embeddings
        logger.info(f"Creating embeddings for {len(all_document_texts)} chunks")
        embeddings = get_embedding_model().encode(all_document_texts)
        embeddings = np.array(embeddings).astype("float32")
        d = embeddings.shape[1]
        
        # Build FAISS index
        index = faiss.IndexFlatL2(d)
        index.add(embeddings)
        
        # Save index and documents
        kb_dir = get_kb_dir(chatbot_id)
        faiss.write_index(index, os.path.join(kb_dir, FAISS_INDEX))
        with open(os.path.join(kb_dir, "documents.json"), "w") as f:
            json.dump(all_documents, f)
        with open(os.path.join(kb_dir, "text_chunks.json"), "w") as f:
            json.dump(all_document_texts, f)
        
        # Update metadata
        metadata = {
            "indexed_files": file_metadata,
            "document_count": len(all_documents),
            "text_chunks_count": len(all_document_texts),
            "last_updated": str(datetime.datetime.now())
        }
        update_indexed_files_metadata(chatbot_id, metadata)
        
        logger.info(f"Built KB for {chatbot_id} with {len(all_documents)} docs")
        return True
    
    except Exception as e:
        logger.error(f"Error building KB for {chatbot_id}: {e}", exc_info=True)
        return False

def load_knowledge_base(chatbot_id: str) -> Tuple[Optional[Any], Optional[List[str]]]:
    """Load existing knowledge base.
    
    Args:
        chatbot_id: Unique identifier for the chatbot
        
    Returns:
        Tuple: (FAISS index, text chunks) if successful, (None, None) otherwise
    """
    try:
        global _FAISS_IMPORTED
        if not _FAISS_IMPORTED:
            import faiss
            _FAISS_IMPORTED = True

        index_path = os.path.join(get_kb_dir(chatbot_id), FAISS_INDEX)
        texts_path = os.path.join(get_kb_dir(chatbot_id), "text_chunks.json")
        
        if not os.path.exists(index_path) or not os.path.exists(texts_path):
            return None, None
        
        index = faiss.read_index(index_path)
        with open(texts_path, "r") as f:
            text_chunks = json.load(f)
        return index, text_chunks
    except Exception as e:
        logger.error(f"Error loading KB for {chatbot_id}: {e}")
        return None, None

def format_content_chunk(item: Dict[str, Any]) -> str:
    """Format a content chunk with section, source and page information.
    
    Args:
        item: Dictionary containing content chunk data
        
    Returns:
        str: Formatted text chunk
    """
    chunk_text = f"Section: {item.get('section', 'Content')} | "
    chunk_text += f"Source: {item.get('source', '')} | "
    if "page" in item:
        chunk_text += f"Page: {item['page']} | "
    chunk_text += item["content"]
    return chunk_text

def format_key_value_chunk(item: Dict[str, Any]) -> str:
    """Format a key-value chunk with source information.
    
    Args:
        item: Dictionary containing key-value data
        
    Returns:
        str: Formatted text chunk
    """
    chunk_parts = [
        f"{key}: {value}"
        for key, value in item.items()
        if isinstance(value, (str, int, float, bool)) and key not in ["source", "index"]
    ]
    if not chunk_parts:
        return ""
    return " | ".join(chunk_parts) + f" | Source: {item.get('source', '')}"

def get_text_chunks(documents: List[Dict[str, Any]]) -> List[str]:
    """Convert documents to text chunks for embedding.
    
    Args:
        documents: List of document dictionaries
        
    Returns:
        List[str]: List of formatted text chunks
    """
    text_chunks = []
    for item in documents:
        text_chunks.append(_process_item(item))
    return text_chunks

def _process_item(item: Any) -> str:
    """Process individual document item into text chunk.
    
    Args:
        item: Document item to process
        
    Returns:
        str: Formatted text chunk
    """
    if isinstance(item, str):
        return item
    if not isinstance(item, dict):
        return str(item)
    
    if "content" in item and isinstance(item["content"], str):
        return _format_content_chunk(item)
    return _format_key_value_chunk(item)

def _format_content_chunk(item: Dict[str, Any]) -> str:
    """Format dictionary with content field.
    
    Args:
        item: Dictionary containing content data
        
    Returns:
        str: Formatted text chunk
    """
    chunk_parts = [
        f"Section: {item.get('section', 'Content')}",
        f"Source: {item.get('source', '')}"
    ]
    if "page" in item:
        chunk_parts.append(f"Page: {item['page']}")
    chunk_parts.append(item["content"])
    return " | ".join(chunk_parts)

def _format_key_value_chunk(item: Dict[str, Any]) -> str:
    """Format dictionary without content field.
    
    Args:
        item: Dictionary containing key-value data
        
    Returns:
        str: Formatted text chunk
    """
    chunk_parts = [
        f"{key}: {value}"
        for key, value in item.items()
        if isinstance(value, (str, int, float, bool)) and key not in ["source", "index"]
    ]
    if not chunk_parts:
        return ""
    return " | ".join(chunk_parts) + f" | Source: {item.get('source', '')}"

def update_indexed_files_metadata(chatbot_id: str, metadata: Dict[str, Any]) -> None:
    """Update metadata file with new information.
    
    Args:
        chatbot_id: Unique identifier for the chatbot
        metadata: Dictionary containing metadata to save
    """
    metadata_path = os.path.join(get_kb_dir(chatbot_id), "metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

def search_kb(chatbot_id: str, query: str, k: int = 5) -> List[str]:
    """Search knowledge base for relevant documents.
    
    Args:
        chatbot_id: Unique identifier for the chatbot
        query: Search query string
        k: Number of results to return (default: 5)
        
    Returns:
        List[str]: List of relevant document chunks
    """
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                         "../kb_storage", chatbot_id)
    
    if not os.path.exists(data_dir):
        logger.warning(f"KB directory {data_dir} does not exist")
        return []
    
    index, documents = load_knowledge_base(chatbot_id)
    if index is None or documents is None:
        logger.warning(f"Failed to load KB for {chatbot_id}")
        return []
    
    try:
        query_embedding = get_embedding_model().encode([query])
        query_embedding = np.array(query_embedding).astype("float32")
        
        distances, indices = index.search(query_embedding, min(k, len(documents)))
        logger.info("KB search completed")
        return [documents[idx] for idx in indices[0]]
    except Exception as e:
        logger.error(f"Search error for {chatbot_id}: {e}")
        return []
    
def rebuild_kb_after_upload(chatbot_id: str) -> bool:
    """Rebuild knowledge base after files have been uploaded.
    
    Scans both knowledge_bases and scrapped_files directories for any supported files
    and re-indexes them using build_knowledge_base.
    
    Args:
        chatbot_id: Unique identifier for the chatbot
        
    Returns:
        bool: True if rebuild was successful, False otherwise
    """
    file_paths = _collect_supported_files(chatbot_id)
    if not file_paths:
        logger.warning(f"No supported files found for {chatbot_id}")
        return False
    
    logger.info(f"Rebuilding KB for {chatbot_id} from {len(file_paths)} files")
    return build_knowledge_base(chatbot_id, file_paths)

def _get_scan_directories(chatbot_id: str) -> tuple[str, str]:
    """Get directories to scan for files.
    
    Args:
        chatbot_id: Unique identifier for the chatbot
        
    Returns:
        tuple: (knowledge base directory, scrapped files directory)
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return (
        os.path.join(base_dir, "../knowledge_bases", chatbot_id),
        os.path.join(base_dir, "../scrapped_files", chatbot_id)
    )

def _is_valid_file(fname: str, full_path: str) -> bool:
    """Check if file should be included in processing.
    
    Args:
        fname: Filename to check
        full_path: Full path to the file
        
    Returns:
        bool: True if file should be processed, False otherwise
    """
    if fname.startswith('.') or fname.startswith('~$'):
        return False
    return any(full_path.lower().endswith(ext) for ext in SUPPORTED_EXTENSIONS)


def _collect_supported_files(chatbot_id: str) -> list[str]:
    """Collect all supported files from both directories.
    
    Args:
        chatbot_id: Unique identifier for the chatbot
        
    Returns:
        list: List of file paths to process
    """
    kb_dir, scrapped_dir = _get_scan_directories(chatbot_id)
    file_paths = []
    
    for root_dir in (kb_dir, scrapped_dir):
        if not os.path.exists(root_dir):
            continue
        for file_path in Path(root_dir).rglob('*'):
            if file_path.is_file() and _is_valid_file(file_path.name, str(file_path)):
                file_paths.append(str(file_path))
    
    return file_paths