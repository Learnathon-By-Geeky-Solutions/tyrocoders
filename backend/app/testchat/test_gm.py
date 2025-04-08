#!/usr/bin/env python
import os
import json
import re
import asyncio
import sqlite3
import requests
import websockets
import numpy as np
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

# ---------------------------
# SETUP: Sample Data Creation
# ---------------------------
# Create a directory to store sample files
os.makedirs("sample_data", exist_ok=True)

# --- Markdown File ---
markdown_data = """
# E-commerce Products

## Product: Widget E
- **Description:** An eco-friendly widget.
- **Price:** $14.99
- **Category:** Gadgets

## Product: Gizmo F
- **Description:** A durable gizmo.
- **Price:** $39.99
- **Category:** Gadgets
"""
md_path = "sample_data/products.md"
with open(md_path, "w") as f:
    f.write(markdown_data.strip())
print(f"Markdown sample created at {md_path}")

# --- CSV File ---
csv_data = """id,name,description,price,category
1,Widget G,A compact widget,12.99,Gadgets
2,Gizmo H,A versatile gizmo,22.99,Gadgets
"""
csv_path = "sample_data/products.csv"
with open(csv_path, "w") as f:
    f.write(csv_data)
print(f"CSV sample created at {csv_path}")

# --- XLSX File ---
xlsx_df = pd.DataFrame({
    "id": [1, 2],
    "name": ["Widget I", "Gizmo J"],
    "description": ["A lightweight widget", "A powerful gizmo"],
    "price": [16.99, 27.99],
    "category": ["Gadgets", "Gadgets"]
})
xlsx_path = "sample_data/products.xlsx"
xlsx_df.to_excel(xlsx_path, index=False)
print(f"XLSX sample created at {xlsx_path}")

# ---------------------------
# BUILD KNOWLEDGE BASE (KB)
# ---------------------------
documents = []

# --- Load JSON ---
# (If you have a JSON file, uncomment and adjust as needed)
json_path = "sample_data/product_pages.json"
if os.path.exists(json_path):
    with open(json_path, "r") as f:
        products_json = json.load(f)
    for prod in products_json:
        # Assuming the JSON structure has these keys:
        doc = (
            f"URL: {prod['url']}\n"
            f"Markdown: {prod['markdown']}\n"
            f"Full Markdown Length: {prod['full_markdown_length']}\n"
            f"Fit Markdown Length: {prod['fit_markdown_length']}\n"
            f"Links: {prod['links']}"
        )
        documents.append(doc)

# --- Load Markdown ---
with open(md_path, "r") as f:
    md_content = f.read()
# Simple parsing: split markdown by product sections (assuming "## Product:" starts each product)
md_products = re.split(r"##\s*Product:", md_content)
for prod in md_products[1:]:  # skip header section
    lines = prod.strip().splitlines()
    name = lines[0].strip()
    details = " ".join(line.strip("- ").strip() for line in lines[1:])
    doc = f"Name: {name}. {details}"
    documents.append(doc)

# --- Load CSV ---
csv_df = pd.read_csv(csv_path)
for _, row in csv_df.iterrows():
    doc = f"ID: {row['id']}. Name: {row['name']}. Description: {row['description']}. Price: {row['price']}. Category: {row['category']}."
    documents.append(doc)

# --- Load XLSX ---
xlsx_df = pd.read_excel(xlsx_path)
for _, row in xlsx_df.iterrows():
    doc = f"ID: {row['id']}. Name: {row['name']}. Description: {row['description']}. Price: {row['price']}. Category: {row['category']}."
    documents.append(doc)

print(f"Total documents loaded from all sources: {len(documents)}")

# ---------------------------
# EMBEDDING & INDEX CREATION
# ---------------------------
# Load a Sentence Transformer model to embed text.
embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Create embeddings for all documents.
embeddings = embedding_model.encode(documents)
embeddings = np.array(embeddings).astype("float32")

# Initialize FAISS index for similarity search.
d = embeddings.shape[1]
index = faiss.IndexFlatL2(d)
index.add(embeddings)

print(f"Knowledge base index built with {len(documents)} documents.")

def search_kb(query, k=1000):
    """
    Given a query, embed it and retrieve the top-k most similar documents.
    Returns:
      results (list): List of matching document texts.
      distances (list): List of corresponding distances.
    """
    query_embedding = embedding_model.encode([query])
    query_embedding = np.array(query_embedding).astype("float32")
    distances, indices = index.search(query_embedding, k)
    results = [documents[idx] for idx in indices[0]]
    return results, distances[0]

# ---------------------------
# Gemini API Integration
# ---------------------------
# Replace with your valid Gemini API key
GEMINI_API_KEY = "AIzaSyA369Ut5Cyl13bNVzuQZzzIPG_PDBBPhTU"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

def ask_llm(query):
    """
    Retrieve context from the KB and use it to form a prompt.
    Call the Gemini API and return the candidate's generated answer.
    """
    # Get relevant context from the knowledge base.
    context_docs, _ = search_kb(query, k=2)
    context_text = "\n".join(context_docs)

    # Build prompt with context and the user query.
    prompt = f"Use the following information to answer the question.\n\nContext:\n{context_text}\n\nQuestion: {query}\nAnswer:"

    # Prepare the payload.
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
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
# WEBSOCKET SERVER
# ---------------------------
async def process_query(websocket):
    """
    For each message (query) received from a client, process it using the ask_llm function and send back the answer.
    """
    try:
        async for message in websocket:
            print("Received query:", message, flush=True)
            # Use the ask_llm function to generate an answer.
            answer = ask_llm(message)
            # Send the generated answer back to the client.
            await websocket.send(answer)
            # Optionally send an "[END]" marker.
            await websocket.send("[END]")
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected", flush=True)
    except Exception as e:
        print(f"Error: {e}", flush=True)

async def main():
    port = int(os.environ.get('PORT', 8090))
    print("WebSocket server starting", flush=True)
    async with websockets.serve(
        process_query,
        "0.0.0.0",
        port
    ) as server:
        print(f"WebSocket server running on port {port}", flush=True)
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
