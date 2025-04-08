import re
import pandas as pd
import os
import json
import yaml

def detect_file_type(path):
    """Detect file type based on extension."""
    _, ext = os.path.splitext(path)
    return ext.lower()

def load_data(path, **kwargs):
    """Dynamic loader that detects file type and calls appropriate loader."""
    file_type = detect_file_type(path)
    
    loaders = {
        '.md': load_markdown,
        '.markdown': load_markdown,
        '.csv': load_csv,
        '.xlsx': load_excel,
        '.xls': load_excel,
        '.json': load_json,
        '.yaml': load_yaml,
        '.yml': load_yaml,
        '.txt': load_text
    }
    
    if file_type in loaders:
        return loaders[file_type](path, **kwargs)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

def load_markdown(path, product_pattern=r"##\s*Product:", **kwargs):
    """Load Markdown file and extract product sections with configurable pattern."""
    with open(path, "r", encoding='utf-8') as f:
        md_content = f.read()
    
    docs = []
    # Split by the product pattern (customizable)
    md_sections = re.split(product_pattern, md_content)
    
    for section in md_sections[1:]:  # Skip first empty section if present
        lines = section.strip().splitlines()
        if not lines:
            continue
        
        name = lines[0].strip()
        details = " ".join(line.strip("- ").strip() for line in lines[1:])
        docs.append(f"Name: {name}. {details}")
    
    return docs

def load_csv(path, id_field='id', **kwargs):
    """Load CSV file with configurable column mapping."""
    docs = []
    df = pd.read_csv(path, **kwargs)
    
    # Use kwargs to determine fields to include
    fields = kwargs.get('fields', df.columns)
    
    for _, row in df.iterrows():
        doc_parts = []
        for field in fields:
            if field in row and pd.notna(row[field]):
                doc_parts.append(f"{field.capitalize()}: {row[field]}")
        
        docs.append(". ".join(doc_parts) + ".")
    
    return docs

def load_excel(path, sheet_name=0, **kwargs):
    """Load Excel file with configurable sheet selection."""
    docs = []
    df = pd.read_excel(path, sheet_name=sheet_name, **kwargs)
    
    # Use kwargs to determine fields to include
    fields = kwargs.get('fields', df.columns)
    
    for _, row in df.iterrows():
        doc_parts = []
        for field in fields:
            if field in row and pd.notna(row[field]):
                doc_parts.append(f"{field.capitalize()}: {row[field]}")
        
        docs.append(". ".join(doc_parts) + ".")
    
    return docs

def load_json(path, **kwargs):
    """Load JSON file and convert to document strings."""
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    docs = []
    
    # Handle both list and dict formats
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                doc_parts = []
                for key, value in item.items():
                    if value is not None:
                        doc_parts.append(f"{key.capitalize()}: {value}")
                docs.append(". ".join(doc_parts) + ".")
    elif isinstance(data, dict):
        # Handle nested structures
        flat_items = flatten_dict(data, **kwargs)
        for item in flat_items:
            docs.append(item)
    
    return docs

def flatten_dict(d, parent_key='', sep='.', **kwargs):
    """Flatten nested dictionary structure."""
    items = []
    
    if isinstance(d, dict):
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            
            if isinstance(v, dict):
                items.extend(flatten_dict(v, new_key, sep))
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    if isinstance(item, dict):
                        item_parts = []
                        for ik, iv in item.items():
                            if iv is not None:
                                item_parts.append(f"{ik.capitalize()}: {iv}")
                        items.append(". ".join(item_parts) + ".")
            else:
                if v is not None:
                    items.append(f"{new_key.capitalize()}: {v}")
    
    return items

def load_yaml(path, **kwargs):
    """Load YAML file and convert to document strings."""
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Reuse the JSON loader logic as YAML structure is similar
    docs = []
    
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                doc_parts = []
                for key, value in item.items():
                    if value is not None:
                        doc_parts.append(f"{key.capitalize()}: {value}")
                docs.append(". ".join(doc_parts) + ".")
    elif isinstance(data, dict):
        flat_items = flatten_dict(data, **kwargs)
        for item in flat_items:
            docs.append(item)
    
    return docs

def load_text(path, delimiter="\n\n", **kwargs):
    """Load text file with configurable delimiter for documents."""
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by delimiter
    chunks = content.split(delimiter)
    docs = [chunk.strip() for chunk in chunks if chunk.strip()]
    
    return docs

# Example usage:
# documents = load_data('products.csv', fields=['name', 'description', 'price'])
# documents = load_data('inventory.xlsx', sheet_name='Sheet1')
# documents = load_data('catalog.md', product_pattern=r"#\s*Item:")