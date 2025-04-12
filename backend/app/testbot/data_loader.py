import os
import pandas as pd
import logging
import json
import re
import html
import PyPDF2
import urllib.parse
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

# Configure logging
logger = logging.getLogger(__name__)

def clean_product_description(description: str) -> str:
    """
    Clean product descriptions by removing escape sequences and special characters,
    preserving only plain text content
    """
    if not isinstance(description, str):
        return ""
    
    # Decode HTML entities
    text = html.unescape(description)
    
    # Replace non-breaking space entities
    text = text.replace("&nbsp;", " ")
    
    # Convert escape sequences to their actual representation
    text = text.encode().decode('unicode_escape')
    
    # Remove excessive whitespace (including tabs and newlines)
    text = re.sub(r'\s+', ' ', text)
    
    # Clean up common formatting artifacts
    text = text.replace('• ', '')
    text = text.replace('\\t', '')
    
    return text.strip()


def parse_size_chart(description: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Extract size chart information from product descriptions
    """
    if not isinstance(description, str):
        return {}
    
    size_chart = {}
    # Look for size chart section
    chart_match = re.search(r'Size Chart.*?(\n\n+|$)', description, re.DOTALL)
    
    if chart_match:
        chart_section = chart_match.group(0)
        
        # Find table rows
        rows = re.findall(r'\n\n(\d+)\n(\d+)\n([\d.]+)\n([\d.]+)\n([\d.]+)\n([\d.]+)\n([\d.]+)\n([\d.]+)', chart_section)
        
        if rows:
            size_chart["sizes"] = []
            for row in rows:
                size_chart["sizes"].append({
                    "size": row[0],
                    "waist": row[1],
                    "length": row[2],
                    "hip": row[3],
                    "thigh": row[4],
                    "leg_opening": row[5],
                    "front_rise": row[6],
                    "back_rise": row[7]
                })
    
    return size_chart

def extract_product_features(description: str) -> List[str]:
    """
    Extract product features from bulleted lists in descriptions
    """
    if not isinstance(description, str):
        return []
    
    # Look for features section
    features_match = re.search(r'Features:(.*?)(?:\n\n|$)', description, re.DOTALL)
    if not features_match:
        return []
    
    features_section = features_match.group(1)
    
    # Find all list items
    feature_items = re.findall(r'(?:\n\s*\\t|\n\s*•|\n\s*-)\s*(.*?)(?=\n\s*\\t|\n\s*•|\n\s*-|\n\n|$)', features_section, re.DOTALL)
    
    # Clean up each feature
    cleaned_features = [item.strip() for item in feature_items if item.strip()]
    
    return cleaned_features

def clean_product_data(product: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean and structure product data
    """
    clean_product = product.copy()
    
    # Clean description
    if "description" in clean_product:
        original_description = clean_product["description"]
        clean_product["description"] = clean_product_description(original_description)
        
        # Extract structured data from description
        clean_product["features"] = extract_product_features(original_description)
        size_chart = parse_size_chart(original_description)
        if size_chart:
            clean_product["size_chart"] = size_chart
    
    # Handle price fields
    if "discountedPrice" in clean_product:
        try:
            clean_product["discountedPrice"] = float(clean_product["discountedPrice"])
        except (ValueError, TypeError):
            pass
    
    # Clean product name
    if "name" in clean_product:
        clean_product["name"] = html.unescape(clean_product["name"]).strip()
    
    # Ensure URL is valid
    if "url" in clean_product and clean_product["url"]:
        clean_product["url"] = clean_product["url"].strip()
    
    return clean_product

def clean_text(text: str) -> str:
    """
    Clean text while preserving URLs and links
    """
    if not isinstance(text, str):
        return text
    
    # Preserve URLs by temporarily replacing them
    url_pattern = r'(https?://[^\s]+)'
    urls = re.findall(url_pattern, text)
    placeholders = {f"__URL_{i}__": url for i, url in enumerate(urls)}
    
    for placeholder, url in placeholders.items():
        text = text.replace(url, placeholder)
    
    # Decode HTML entities
    text = html.unescape(text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Restore URLs
    for placeholder, url in placeholders.items():
        text = text.replace(placeholder, url)
    
    return text

def load_file(file_path: str) -> List[Dict[str, Any]]:
    """Load documents from various file types and convert to JSON"""
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return []
    
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if ext == '.md':
            return load_markdown(file_path)
        elif ext == '.csv':
            return load_csv(file_path)
        elif ext == '.xlsx' or ext == '.xls':
            return load_excel(file_path)
        elif ext == '.json':
            return load_json(file_path)
        elif ext == '.pdf':
            return load_pdf(file_path)
        else:
            logger.warning(f"Unsupported file type: {file_path}")
            return []
    except Exception as e:
        logger.error(f"Error loading file {file_path}: {e}")
        return []

def load_markdown(file_path: str) -> List[Dict[str, Any]]:
    """
    Load markdown files and convert to JSON objects
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by headers or paragraphs
        chunks = []
        lines = content.split('\n')
        current_chunk = []
        current_header = "Content"
        
        for line in lines:
            # If we encounter a header, start a new chunk
            if line.startswith('#'):
                if current_chunk:
                    text_content = '\n'.join(current_chunk)
                    chunks.append({
                        "section": current_header,
                        "content": text_content,
                        "source": os.path.basename(file_path)
                    })
                    current_chunk = []
                current_header = line.lstrip('#').strip()
            
            current_chunk.append(line)
            
            # If the chunk gets too large, split it
            if len('\n'.join(current_chunk)) > 1000:
                text_content = '\n'.join(current_chunk)
                chunks.append({
                    "section": current_header,
                    "content": text_content,
                    "source": os.path.basename(file_path)
                })
                current_chunk = []
        
        # Add the last chunk if it exists
        if current_chunk:
            text_content = '\n'.join(current_chunk)
            chunks.append({
                "section": current_header,
                "content": text_content,
                "source": os.path.basename(file_path)
            })
        
        return chunks
    except Exception as e:
        logger.error(f"Error loading markdown: {e}")
        return []

def load_csv(file_path: str) -> List[Dict[str, Any]]:
    """
    Load CSV files and convert rows to JSON objects
    """
    try:
        df = pd.read_csv(file_path)
        
        # Convert each row to a JSON object
        chunks = []
        for idx, row in df.iterrows():
            row_dict = {}
            
            # Process each column value
            for col, val in row.items():
                if pd.notna(val):
                    row_dict[col] = val
            
            # Add metadata
            row_dict["row_index"] = idx
            row_dict["source"] = os.path.basename(file_path)
            
            # Apply product-specific cleaning if this is product data
            if any(col in row_dict for col in ["product", "name", "description", "price", "sku"]):
                row_dict = clean_product_data(row_dict)
            
            chunks.append(row_dict)
        
        return chunks
    except Exception as e:
        logger.error(f"Error loading CSV: {e}")
        return []

def load_excel(file_path: str) -> List[Dict[str, Any]]:
    """
    Load Excel files and convert rows to JSON objects
    """
    try:
        # Read all sheets
        xl = pd.ExcelFile(file_path)
        chunks = []
        
        for sheet_name in xl.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # Convert each row to a JSON object
            for idx, row in df.iterrows():
                row_dict = {}
                
                # Process each column value
                for col, val in row.items():
                    if pd.notna(val):
                        row_dict[col] = val
                
                # Add metadata
                row_dict["sheet_name"] = sheet_name
                row_dict["row_index"] = idx
                row_dict["source"] = os.path.basename(file_path)
                
                # Apply product-specific cleaning if this is product data
                if any(col in row_dict for col in ["product", "name", "description", "price", "sku"]):
                    row_dict = clean_product_data(row_dict)
                
                chunks.append(row_dict)
        
        return chunks
    except Exception as e:
        logger.error(f"Error loading Excel: {e}")
        return []

def load_json(file_path: str) -> List[Dict[str, Any]]:
    """
    Load JSON files and convert to a list of dictionaries
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        chunks = []
        
        # Handle both JSON arrays and objects
        if isinstance(data, list):
            # If it's already a list of dictionaries
            for idx, item in enumerate(data):
                if isinstance(item, dict):
                    item_copy = item.copy()
                    item_copy["source"] = os.path.basename(file_path)
                    item_copy["index"] = idx
                    
                    # Apply product-specific cleaning if this is product data
                    if any(key in item_copy for key in ["product", "name", "description", "price", "sku"]):
                        item_copy = clean_product_data(item_copy)
                    
                    chunks.append(item_copy)
                else:
                    # If it's a list of non-dictionary values
                    chunks.append({
                        "value": item,
                        "index": idx,
                        "source": os.path.basename(file_path)
                    })
        elif isinstance(data, dict):
            # If it's a single dictionary, add it as one chunk
            data_copy = data.copy()
            data_copy["source"] = os.path.basename(file_path)
            
            # Apply product-specific cleaning if this is product data
            if any(key in data_copy for key in ["product", "name", "description", "price", "sku"]):
                data_copy = clean_product_data(data_copy)
            
            chunks.append(data_copy)
            
            # Alternatively, split large dictionaries into smaller chunks
            if len(json.dumps(data)) > 10000:
                logger.info(f"Large JSON object detected in {file_path}, splitting into keys")
                for key, value in data.items():
                    chunk = {
                        "key": key,
                        "value": value,
                        "source": os.path.basename(file_path)
                    }
                    
                    # Apply product-specific cleaning if this is product data
                    if isinstance(value, dict) and any(k in value for k in ["product", "name", "description", "price", "sku"]):
                        chunk["value"] = clean_product_data(value)
                    
                    chunks.append(chunk)
        else:
            chunks.append({
                "value": data,
                "source": os.path.basename(file_path)
            })
            
        return chunks
    except Exception as e:
        logger.error(f"Error loading JSON: {e}")
        return []

def load_pdf(file_path: str) -> List[Dict[str, Any]]:
    """
    Load PDF files and extract text from pages
    """
    try:
        chunks = []
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Process each page
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                
                if text:
                    # Split text into manageable chunks
                    paragraphs = text.split('\n\n')
                    for i, paragraph in enumerate(paragraphs):
                        if paragraph.strip():
                            chunks.append({
                                "page": page_num + 1,
                                "paragraph": i + 1,
                                "content": paragraph.strip(),
                                "source": os.path.basename(file_path)
                            })
        
        # Handle empty PDFs or images-only PDFs
        if not chunks:
            chunks.append({
                "content": "PDF contains no extractable text (may contain only images)",
                "source": os.path.basename(file_path),
                "page_count": len(pdf_reader.pages)
            })
            
        return chunks
    except Exception as e:
        logger.error(f"Error loading PDF: {e}")
        return []

def process_product_documents(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process a list of documents that may contain product data
    """
    processed_docs = []
    for doc in documents:
        # Check if this looks like product data
        if any(key in doc for key in ["product", "name", "description", "price", "sku"]):
            processed_docs.append(clean_product_data(doc))
        else:
            processed_docs.append(doc)
    
    return processed_docs

def get_json_string(data: List[Dict[str, Any]]) -> str:
    """Convert the loaded data to a JSON string"""
    return json.dumps(data, indent=2, ensure_ascii=False)

def batch_process_directory(directory_path: str, output_path: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
    """
    Process all supported files in a directory and return consolidated data
    """
    results = {}
    
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ['.md', '.csv', '.xlsx', '.xls', '.json', '.pdf']:
                logger.info(f"Processing {file_path}")
                file_data = load_file(file_path)
                results[filename] = file_data
    
    # Optionally save results to a JSON file
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    
    return results

def load_product_data_from_text(text_content: str, source_name: str = "text_input") -> List[Dict[str, Any]]:
    """
    Parse product data from text input that might contain JSON product data
    """
    try:
        # Try to parse as JSON first
        pattern = r'(?:\{[^{}]*\})'
        potential_json_objects = re.findall(pattern, text_content)
        
        products = []
        for json_str in potential_json_objects:
            try:
                product = json.loads(json_str)
                if isinstance(product, dict):
                    # Add source metadata
                    product["source"] = source_name
                    # Clean the product data
                    products.append(clean_product_data(product))
            except json.JSONDecodeError:
                continue
        
        if products:
            return products
        
        # If no valid JSON objects found, try to parse structured text
        # This is a simplified approach - would need more sophisticated parsing for real text
        chunks = text_content.split("Document ")
        
        for chunk in chunks:
            if not chunk.strip():
                continue
                
            # Try to extract a JSON object from the text
            json_pattern = r'\{.*?\}'
            json_match = re.search(json_pattern, chunk, re.DOTALL)
            
            if json_match:
                try:
                    product = json.loads(json_match.group(0))
                    if isinstance(product, dict):
                        product["source"] = source_name
                        products.append(clean_product_data(product))
                except json.JSONDecodeError:
                    # If JSON parsing fails, try to extract key-value pairs
                    lines = chunk.strip().split('\n')
                    product = {"source": source_name}
                    
                    for line in lines:
                        if ':' in line:
                            key, value = line.split(':', 1)
                            product[key.strip("'\"")] = value.strip()
                    
                    if product:
                        products.append(clean_product_data(product))
        
        return products
            
    except Exception as e:
        logger.error(f"Error parsing product data from text: {e}")
        return []