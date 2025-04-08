# kb.py
import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from data_loader import load_markdown, load_csv, load_xlsx
from config import KB_STORAGE_DIR

# Load the embedding model (make sure you have the model installed)
embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def get_kb_file_paths(chatbot_id):
    index_path = os.path.join(KB_STORAGE_DIR, f"{chatbot_id}_index.faiss")
    docs_path = os.path.join(KB_STORAGE_DIR, f"{chatbot_id}_docs.json")
    return index_path, docs_path

def build_kb(chatbot_id, data_paths):
    """Builds a KB (documents and FAISS index) for a specific chatbot using the provided file paths."""
    documents = []
    for path in data_paths:
        if path.endswith('.md'):
            documents.extend(load_markdown(path))
        elif path.endswith('.csv'):
            documents.extend(load_csv(path))
        elif path.endswith('.xlsx'):
            documents.extend(load_xlsx(path))
        else:
            print(f"Unsupported file type: {path}")
    if not documents:
        print(f"No documents loaded for {chatbot_id}.")
        return None, None
    # Create embeddings
    embeddings = embedding_model.encode(documents)
    embeddings = np.array(embeddings).astype("float32")
    d = embeddings.shape[1]
    # Create FAISS index and add embeddings
    index = faiss.IndexFlatL2(d)
    index.add(embeddings)
    return index, documents

def save_kb(chatbot_id, index, documents):
    index_path, docs_path = get_kb_file_paths(chatbot_id)
    faiss.write_index(index, index_path)
    with open(docs_path, "w") as f:
        json.dump(documents, f)

def load_kb(chatbot_id):
    index_path, docs_path = get_kb_file_paths(chatbot_id)
    if not os.path.exists(index_path) or not os.path.exists(docs_path):
        return None, None
    index = faiss.read_index(index_path)
    with open(docs_path, "r") as f:
        documents = json.load(f)
    return index, documents

def get_or_create_kb(chatbot_id, data_paths):
    """Return an existing KB or build and save a new one if it does not exist."""
    index, documents = load_kb(chatbot_id)
    if index is None or documents is None:
        print(f"Building KB for {chatbot_id}...")
        index, documents = build_kb(chatbot_id, data_paths)
        if index is not None and documents is not None:
            save_kb(chatbot_id, index, documents)
    else:
        print(f"Loaded existing KB for {chatbot_id} with {len(documents)} documents.")
    return index, documents

def search_kb(chatbot_id, query, k=1000):
    """Given a query and chatbot ID, embed the query and retrieve the top-k similar documents."""
    index, documents = load_kb(chatbot_id)
    if index is None or documents is None:
        return [], []
    query_embedding = embedding_model.encode([query])
    query_embedding = np.array(query_embedding).astype("float32")
    distances, indices = index.search(query_embedding, k)
    results = [documents[idx] for idx in indices[0]]
    return results, distances[0]
