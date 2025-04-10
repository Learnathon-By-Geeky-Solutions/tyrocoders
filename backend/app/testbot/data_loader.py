import os
import pandas as pd
import logging
from typing import List, Optional

# Configure logging
logger = logging.getLogger(__name__)

def load_file(file_path: str) -> List[str]:
    """Load documents from various file types"""
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return []
    
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if ext == '.md':
            return load_markdown(file_path)
        elif ext == '.csv':
            return load_csv(file_path)
        elif ext == '.xlsx':
            return load_excel(file_path)
        else:
            logger.warning(f"Unsupported file type: {file_path}")
            return []
    except Exception as e:
        logger.error(f"Error loading file {file_path}: {e}")
        return []

def load_markdown(file_path: str) -> List[str]:
    """
    Load and chunk markdown files
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by headers or paragraphs
        chunks = []
        lines = content.split('\n')
        current_chunk = []
        
        for line in lines:
            # If we encounter a header, start a new chunk
            if line.startswith('#'):
                if current_chunk:
                    chunks.append('\n'.join(current_chunk))
                    current_chunk = []
            
            current_chunk.append(line)
            
            # If the chunk gets too large, split it
            if len('\n'.join(current_chunk)) > 1000:
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
        
        # Add the last chunk if it exists
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks
    except Exception as e:
        logger.error(f"Error loading markdown: {e}")
        return []

def load_csv(file_path: str) -> List[str]:
    """
    Load CSV files and convert rows to text chunks
    """
    try:
        df = pd.read_csv(file_path)
        
        # Convert each row to a text chunk
        chunks = []
        for _, row in df.iterrows():
            # Format row as key-value pairs
            row_text = " | ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
            chunks.append(row_text)
        
        return chunks
    except Exception as e:
        logger.error(f"Error loading CSV: {e}")
        return []

def load_excel(file_path: str) -> List[str]:
    """
    Load Excel files and convert rows to text chunks
    """
    try:
        # Read all sheets
        xl = pd.ExcelFile(file_path)
        chunks = []
        
        for sheet_name in xl.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # Add sheet name as context
            sheet_prefix = f"Sheet: {sheet_name} | "
            
            # Convert each row to a text chunk
            for _, row in df.iterrows():
                # Format row as key-value pairs with sheet name
                row_text = sheet_prefix + " | ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                chunks.append(row_text)
        
        return chunks
    except Exception as e:
        logger.error(f"Error loading Excel: {e}")
        return []