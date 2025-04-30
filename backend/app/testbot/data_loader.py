"""
File Processor Module

This module provides functionality to load and process various document types (Markdown, CSV, Excel)
into text chunks that can be used for further processing or analysis.

The module supports:
- Markdown files (.md): Chunks by headers or paragraph blocks
- CSV files (.csv): Converts each row to a formatted text chunk
- Excel files (.xlsx): Processes all sheets, converting rows to text chunks with sheet context

Each file type is processed with a specialized loading function that handles the specific format
requirements and error conditions. The module implements logging to track file processing
status and errors.

Functions:
    load_file(file_path: str) -> List[str]:
        Entry point for document loading. Determines file type and routes to appropriate loader.
        
    load_markdown(file_path: str) -> List[str]:
        Loads markdown files and chunks them by headers or large paragraph blocks.
        
    load_csv(file_path: str) -> List[str]:
        Loads CSV files and converts rows to formatted text chunks.
        
    load_excel(file_path: str) -> List[str]:
        Loads Excel files, processing all sheets and converting rows to text chunks.

Requirements:
    - pandas: For handling CSV and Excel files
    - logging: For tracking processing status and errors
    - os: For file path operations
    - typing: For type annotations

Error Handling:
    - Validates file existence before processing
    - Catches and logs exceptions during file loading and processing
    - Returns empty list when errors occur to allow graceful continuation

Usage Example:
    ```python
    from file_processor import load_file
    
    # Load a markdown file
    md_chunks = load_file('documentation.md')
    
    # Load a CSV file
    csv_chunks = load_file('data.csv')
    
    # Load an Excel file
    excel_chunks = load_file('spreadsheet.xlsx')
    ```
"""
import os
import pandas as pd
import logging
from typing import List, Optional

# Configure logging
logger = logging.getLogger(__name__)

def load_file(file_path: str) -> List[str]:
    """
    Load documents from various file types and convert to text chunks.
    
    This function serves as the main entry point for document loading. It determines
    the file type based on extension and routes to the appropriate specialized loader.
    
    Args:
        file_path (str): Path to the document file to be loaded
        
    Returns:
        List[str]: List of text chunks extracted from the document
        
    Raises:
        No exceptions are raised, as errors are caught and logged internally
        
    Notes:
        - Currently supports .md, .csv, and .xlsx file formats
        - Returns empty list if file doesn't exist or has unsupported format
        - All exceptions during loading are caught, logged, and an empty list is returned
    """
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
    Load and chunk markdown files by headers or large paragraph blocks.
    
    This function reads a markdown file and splits it into logical chunks based on:
    1. Headers (lines starting with #)
    2. Size limits (chunks exceeding 1000 characters)
    
    Args:
        file_path (str): Path to the markdown file
        
    Returns:
        List[str]: List of markdown chunks
        
    Notes:
        - Each header starts a new chunk
        - Chunks are also split if they exceed 1000 characters
        - Empty chunks are not added to the result
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        chunks = []
        lines = content.split('\n')
        current_chunk = []
        
        for line in lines:
            # Start a new chunk if a header is encountered
            if line.startswith('#') and current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
                
            current_chunk.append(line)
            
            # Split chunk if it exceeds the size limit
            if len('\n'.join(current_chunk)) > 1000:
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
                
        # Append the remaining chunk if any
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
            
        return chunks
    except Exception as e:
        logger.error("Error loading markdown: %s", e)
        return []


def load_csv(file_path: str) -> List[str]:
    """
    Load CSV files and convert rows to text chunks.
    
    Each row in the CSV is converted to a text chunk formatted as key-value pairs
    separated by pipe characters (|).
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        List[str]: List of text chunks, each representing a row from the CSV
        
    Notes:
        - NaN/empty values are excluded from the output
        - Each chunk follows the format: "column1: value1 | column2: value2 | ..."
        - Uses pandas for CSV parsing to handle various CSV formats and encodings
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
    Load Excel files and convert rows to text chunks.
    
    Processes all sheets in the Excel file, converting each row to a text chunk
    with the sheet name included as context. Rows are formatted as key-value pairs.
    
    Args:
        file_path (str): Path to the Excel file
        
    Returns:
        List[str]: List of text chunks, each representing a row from the Excel file
        
    Notes:
        - Each chunk includes the sheet name as context
        - NaN/empty values are excluded from the output
        - Each chunk follows format: "Sheet: sheet_name | column1: value1 | column2: value2 | ..."
        - Uses pandas for Excel parsing to handle various Excel formats
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