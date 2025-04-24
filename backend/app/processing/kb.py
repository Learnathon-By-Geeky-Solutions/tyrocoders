import os
import json
import numpy as np
import faiss
import datetime
from pathlib import Path
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple, Optional, Any

from core.config import SUPPORTED_EXTENSIONS
from core.logger import logger
from processing.data_loader import load_file


# New base directory for knowledge bases
BASE_KB_DIR = "./kb_storage"

# Load the embedding model
embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def get_kb_dir(chatbot_id: str) -> str:
    """Get the KB directory for a specific chatbot"""
    kb_dir = os.path.join(BASE_KB_DIR, chatbot_id)
    os.makedirs(kb_dir, exist_ok=True)
    return kb_dir



def get_meta_data_path(chatbot_id: str) -> str:
    """Generate the path for metadata about indexed files"""
    kb_dir = get_kb_dir(chatbot_id)
    return os.path.join(kb_dir, "metadata.json")

def kb_exists(chatbot_id: str) -> bool:
    """Check if knowledge base for chatbot exists"""
    index_path = get_knowledge_index_path(chatbot_id)
    docs_path = get_knowledge_docs_path(chatbot_id)
    return os.path.exists(index_path) and os.path.exists(docs_path)

def get_indexed_files_metadata(chatbot_id: str) -> Dict:
    """Get metadata about previously indexed files"""
    meta_path = get_meta_data_path(chatbot_id)
    if os.path.exists(meta_path):
        with open(meta_path, "r") as f:
            return json.load(f)
    return {}


def should_update_index(chatbot_id: str, file_paths: List[str]) -> bool:
    """Check if the index should be updated based on file modification times or new files"""
    if not kb_exists(chatbot_id):
        return True
    
    metadata = get_indexed_files_metadata(chatbot_id)
    indexed_files = metadata.get("indexed_files", {})
    
    # Check if files have been added or removed
    if set(indexed_files.keys()) != set(file_paths):
        return True
    
    # Check if any files have been modified
    for file_path in file_paths:
        file_mod_time = os.path.getmtime(file_path)
        if file_path not in indexed_files or file_mod_time > indexed_files[file_path]:
            return True
    
    return False


def build_knowledge_base(chatbot_id: str, file_paths: List[str]) -> bool:
    """Build a unified knowledge base from multiple files"""
    try:
        all_documents = []
        all_document_texts = []  # New list to store text representations
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
            
            # Convert structured documents to text format suitable for embedding
            document_texts = get_text_chunks(documents)
            
            all_documents.extend(documents)
            all_document_texts.extend(document_texts)
            file_metadata[file_path] = os.path.getmtime(file_path)
        
        if not all_documents:
            logger.warning(f"No documents loaded from any files for {chatbot_id}")
            return False
        
        # Create embeddings from the text representations
        logger.info(f"Creating embeddings for {len(all_document_texts)} text chunks from {len(file_paths)} files")
        embeddings = embedding_model.encode(all_document_texts)
        embeddings = np.array(embeddings).astype("float32")
        d = embeddings.shape[1]
        
        # Create FAISS index
        index = faiss.IndexFlatL2(d)
        index.add(embeddings)
        
        # Save index, documents, and their text representations
        index_path = get_knowledge_index_path(chatbot_id)
        docs_path = get_knowledge_docs_path(chatbot_id)
        texts_path = get_knowledge_texts_path(chatbot_id)
        
        faiss.write_index(index, index_path)
        with open(docs_path, "w") as f:
            json.dump(all_documents, f)
        with open(texts_path, "w") as f:
            json.dump(all_document_texts, f)
        
        # Update metadata
        metadata = {
            "indexed_files": file_metadata,
            "document_count": len(all_documents),
            "text_chunks_count": len(all_document_texts),
            "last_updated": str(datetime.datetime.now())
        }
        update_indexed_files_metadata(chatbot_id, metadata)
        
        logger.info(f"Built knowledge base for chatbot {chatbot_id} with {len(all_documents)} documents and {len(all_document_texts)} text chunks")
        return True
    
    except Exception as e:
        logger.error(f"Error building knowledge base for {chatbot_id}: {e}", exc_info=True)  # Added exc_info to get stack trace
        return False

def load_knowledge_base(chatbot_id: str) -> Tuple[Optional[Any], Optional[List[str]]]:
    """Load unified knowledge base index and documents"""
    index_path = get_knowledge_index_path(chatbot_id)
    logger.debug(f"Index path {index_path}")
    texts_path = get_knowledge_texts_path(chatbot_id)
    logger.debug(f"Texts path {texts_path}")
    if not os.path.exists(index_path) or not os.path.exists(texts_path):
        return None, None
    
    try:
        index = faiss.read_index(index_path)
        with open(texts_path, "r") as f:
            text_chunks = json.load(f)
        return index, text_chunks
    except Exception as e:
        logger.error(f"Error loading knowledge base for {chatbot_id}: {e}")
        return None, None

def format_content_chunk(item: Dict[str, Any]) -> str:
    chunk_text = f"Section: {item.get('section', 'Content')} | "
    chunk_text += f"Source: {item.get('source', '')} | "
    if "page" in item:
        chunk_text += f"Page: {item['page']} | "
    chunk_text += item["content"]
    return chunk_text

def format_key_value_chunk(item: Dict[str, Any]) -> str:
    chunk_parts = [
        f"{key}: {value}"
        for key, value in item.items()
        if isinstance(value, (str, int, float, bool)) and key not in ["source", "index"]
    ]
    if not chunk_parts:
        return ""
    return " | ".join(chunk_parts) + f" | Source: {item.get('source', '')}"

def get_text_chunks(documents: List[Dict[str, Any]]) -> List[str]:
    """Convert structured data to text chunks for embedding"""
    text_chunks = []

    for item in documents:
        if isinstance(item, dict):
            content = item.get("content")
            if isinstance(content, str):
                text_chunks.append(format_content_chunk(item))
            else:
                chunk_text = format_key_value_chunk(item)
                if chunk_text:
                    text_chunks.append(chunk_text)
        elif isinstance(item, str):
            text_chunks.append(item)
        else:
            text_chunks.append(str(item))

    return text_chunks

def get_knowledge_index_path(chatbot_id: str) -> str:
    """Get the path to the FAISS index file for a chatbot"""
    directory = f"{get_kb_dir(chatbot_id)}"
    os.makedirs(directory, exist_ok=True)
    return os.path.join(directory, "index.faiss")

def get_knowledge_docs_path(chatbot_id: str) -> str:
    """Get the path to the documents file for a chatbot"""
    directory = f"{get_kb_dir(chatbot_id)}"
    os.makedirs(directory, exist_ok=True)
    return os.path.join(directory, "documents.json")

def get_knowledge_texts_path(chatbot_id: str) -> str:
    """Get the path to the text chunks file for a chatbot"""
    directory = f"{get_kb_dir(chatbot_id)}"
    os.makedirs(directory, exist_ok=True)
    return os.path.join(directory, "text_chunks.json")

def update_indexed_files_metadata(chatbot_id: str, metadata: Dict[str, Any]) -> None:
    """Update metadata for indexed files"""
    directory = f"{get_kb_dir(chatbot_id)}"
    os.makedirs(directory, exist_ok=True)
    metadata_path = os.path.join(directory, "metadata.json")
    
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

def search_kb(chatbot_id: str, query: str, k: int = 5) -> List[str]:
    """
    Search knowledge base for a chatbot and return the top results
    """
    # Check if we need to update the knowledge base
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                           "../kb_storage", chatbot_id)
    
    if not os.path.exists(data_dir):
        logger.warning(f"Knowledge base directory {data_dir} does not exist for {chatbot_id}")
        return []
    
    # Get all files in the directory
    # file_paths = []
    # for root, _, files in os.walk(data_dir):
    #     for file in files:
    #         file_path = os.path.join(root, file)
    #         file_paths.append(file_path)
    
    # Check if we need to update the index
    # if should_update_index(chatbot_id, file_paths):
    #     logger.info(f"Building/updating knowledge base for {chatbot_id}")
    #     if not build_knowledge_base(chatbot_id, file_paths):
    #         return []
    
    # Load the knowledge base
    index, documents = load_knowledge_base(chatbot_id)
    if index is None or documents is None:
        logger.warning(f"Failed to load knowledge base for {chatbot_id}")
        return []
    
    # Encode the query
    query_embedding = embedding_model.encode([query])
    query_embedding = np.array(query_embedding).astype("float32")
    
    # Search the index
    try:
        _, indices = index.search(query_embedding, min(k, len(documents)))
        logger.info("Indexes are searched")
        results = [documents[idx] for idx in indices[0]]
        return results
    except Exception as e:
        logger.error(f"Error searching knowledge base for {chatbot_id}: {e}")
        return []

from core.config import SUPPORTED_EXTENSIONS
from processing.kb import build_knowledge_base
import os
import logging

logger = logging.getLogger(__name__)

def rebuild_kb_after_upload(chatbot_id: str) -> bool:
    """
    Rebuild knowledge base after files have been uploaded.
    Scans both knowledge_bases and scrapped_files for any supported files
    and re-indexes them using build_knowledge_base.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    kb_dir = os.path.join(base_dir, "../knowledge_bases", chatbot_id)
    scrapped_dir = os.path.join(base_dir, "../scrapped_files", chatbot_id)

    file_paths = collect_supported_files([kb_dir, scrapped_dir])

    if not file_paths:
        logger.warning(f"No supported files found for chatbot {chatbot_id}")
        return False

    logger.info(f"Rebuilding KB for {chatbot_id} from {len(file_paths)} files")
    return build_knowledge_base(chatbot_id, file_paths)


def collect_supported_files(directories: list) -> list:
    """
    Traverse given directories and collect supported file paths.
    """
    collected_files = []
    for directory in directories:
        if not os.path.exists(directory):
            continue
        for root, _, files in os.walk(directory):
            for fname in files:
                if is_ignored_file(fname):
                    continue
                full_path = os.path.join(root, fname)
                if is_supported_file(full_path):
                    collected_files.append(full_path)
    return collected_files


def is_ignored_file(fname: str) -> bool:
    return fname.startswith('.') or fname.startswith('~$')


def is_supported_file(path: str) -> bool:
    return any(path.lower().endswith(ext) for ext in SUPPORTED_EXTENSIONS)
