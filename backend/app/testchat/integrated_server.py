#!/usr/bin/env python
import os
import json
import re
import asyncio
import requests
import websockets
import numpy as np
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

# Global dictionaries to hold KB indexes and document lists for each chatbot instance.
kb_indexes = {}      # e.g., { "chatbot_A": faiss_index_A, "chatbot_B": faiss_index_B }
kb_documents = {}    # e.g., { "chatbot_A": [doc1, doc2, ...], "chatbot_B": [...] }

# Load the embedding model (ensure you have a proper version installed)
embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# ---------------------------
# Helper Functions to Load Data
# ---------------------------
def load_markdown(path):
    """Load Markdown file and extract product sections."""
    with open(path, "r") as f:
        md_content = f.read()
    docs = []
    # Assume each product section starts with "## Product:"
    md_products = re.split(r"##\s*Product:", md_content)
    for prod in md_products[1:]:
        lines = prod.strip().splitlines()
        if not lines:
            continue
        name = lines[0].strip()
        details = " ".join(line.strip("- ").strip() for line in lines[1:])
        docs.append(f"Name: {name}. {details}")
    return docs

def load_csv(path):
    """Load CSV file and convert rows to document strings."""
    docs = []
    df = pd.read_csv(path)
    for _, row in df.iterrows():
        docs.append(f"ID: {row['id']}. Name: {row['name']}. Description: {row['description']}. Price: {row['price']}. Category: {row['category']}.")
    return docs

def load_xlsx(path):
    """Load XLSX file and convert rows to document strings."""
    docs = []
    df = pd.read_excel(path)
    for _, row in df.iterrows():
        docs.append(f"ID: {row['id']}. Name: {row['name']}. Description: {row['description']}. Price: {row['price']}. Category: {row['category']}.")
    return docs

# ---------------------------
# Build Knowledge Base for Each Chatbot Instance
# ---------------------------
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
        return
    # Create embeddings
    embeddings = embedding_model.encode(documents)
    embeddings = np.array(embeddings).astype("float32")
    d = embeddings.shape[1]
    # Create FAISS index and add embeddings
    index = faiss.IndexFlatL2(d)
    index.add(embeddings)
    # Store in global dictionaries
    kb_indexes[chatbot_id] = index
    kb_documents[chatbot_id] = documents
    print(f"KB built for {chatbot_id} with {len(documents)} documents.")

# ---------------------------
# Sample Data Creation
# ---------------------------
# Create directories for each chatbot instance
os.makedirs("chatbot_data/chatbot_A", exist_ok=True)
os.makedirs("chatbot_data/chatbot_B", exist_ok=True)

# --- Chatbot A Sample Data (Markdown and CSV) ---
markdown_data_A = """
# E-commerce Products

## Product: Widget A
- **Description:** A high-quality widget.
- **Price:** $19.99
- **Category:** Gadgets

## Product: Gizmo A
- **Description:** An advanced gizmo.
- **Price:** $29.99
- **Category:** Gadgets
"""
md_path_A = "chatbot_data/chatbot_A/products.md"
with open(md_path_A, "w") as f:
    f.write(markdown_data_A.strip())

csv_data_A = """id,name,description,price,category
1,Widget B,A compact widget,12.99,Gadgets
2,Gizmo B,A versatile gizmo,22.99,Gadgets
"""
csv_path_A = "chatbot_data/chatbot_A/products.csv"
with open(csv_path_A, "w") as f:
    f.write(csv_data_A)

# --- Chatbot B Sample Data (XLSX) ---
xlsx_df_B = pd.DataFrame({
    "id": [1, 2],
    "name": ["Widget C", "Gizmo C"],
    "description": ["A lightweight widget", "A powerful gizmo"],
    "price": [16.99, 27.99],
    "category": ["Gadgets", "Gadgets"]
})
xlsx_path_B = "chatbot_data/chatbot_B/products.xlsx"
xlsx_df_B.to_excel(xlsx_path_B, index=False)

# Build KBs for each chatbot
build_kb("chatbot_A", [md_path_A, csv_path_A])
build_kb("chatbot_B", [xlsx_path_B])

# ---------------------------
# Query Processing Functions
# ---------------------------
def search_kb(chatbot_id, query, k=1000):
    """
    Given a query and chatbot ID, embed the query and retrieve the top-k similar documents.
    """
    index = kb_indexes.get(chatbot_id)
    documents = kb_documents.get(chatbot_id)
    if index is None or documents is None:
        return [], []
    query_embedding = embedding_model.encode([query])
    query_embedding = np.array(query_embedding).astype("float32")
    distances, indices = index.search(query_embedding, k)
    results = [documents[idx] for idx in indices[0]]
    return results, distances[0]

# ---------------------------
# Gemini API Integration (LLM Call)
# ---------------------------
# Replace with your valid Gemini API key
GEMINI_API_KEY = "AIzaSyA369Ut5Cyl13bNVzuQZzzIPG_PDBBPhTU"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

def ask_llm(prompt):
    """
    Given a prompt, call the Gemini API and return the generated answer.
    """
    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(GEMINI_API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        try:
            result = response.json()
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    answer_text = candidate["content"]["parts"][0].get("text", "").strip()
                    return answer_text if answer_text else "No output returned."
                else:
                    return "No content found in candidate."
            else:
                return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error parsing response: {e}"
    else:
        return f"Error: {response.status_code} {response.text}"

# ---------------------------
# WebSocket Server for Query Processing
# ---------------------------
async def process_query(websocket):
    """
    For each incoming message, process the query using the correct chatbot's KB.
    The client should send a JSON message with 'chatbot_id' and 'query' keys.
    """
    try:
        async for message in websocket:
            print("Received message:", message, flush=True)
            try:
                data = json.loads(message)
                chatbot_id = data.get("chatbot_id")
                query = data.get("query")
                if not chatbot_id or not query:
                    response_text = "Invalid message format. Expected keys: 'chatbot_id' and 'query'."
                else:
                    # Retrieve context from the KB
                    context_docs, _ = search_kb(chatbot_id, query, k=2)
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
        print("Client disconnected", flush=True)
    except Exception as e:
        print(f"Error in process_query: {e}", flush=True)

async def main():
    port = int(os.environ.get('PORT', 8090))
    print("WebSocket server starting on port", port, flush=True)
    async with websockets.serve(process_query, "0.0.0.0", port):
        print("WebSocket server running...", flush=True)
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
