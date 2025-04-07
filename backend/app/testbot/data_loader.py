# data_loader.py
import re
import pandas as pd

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
        docs.append(
            f"ID: {row['id']}. Name: {row['name']}. Description: {row['description']}. Price: {row['price']}. Category: {row['category']}."
        )
    return docs

def load_xlsx(path):
    """Load XLSX file and convert rows to document strings."""
    docs = []
    df = pd.read_excel(path)
    for _, row in df.iterrows():
        docs.append(
            f"ID: {row['id']}. Name: {row['name']}. Description: {row['description']}. Price: {row['price']}. Category: {row['category']}."
        )
    return docs
