import os
import re
import json
import html
import PyPDF2
import docx
import pandas as pd
from core.logger import logger
from typing import List
from pathlib import Path
from bs4 import BeautifulSoup

# Define supported extensions
SUPPORTED_EXTENSIONS = ['.txt', '.md', '.csv', '.xlsx', '.pdf', '.docx', '.json']

import os
import json
import re
import html
import logging
import pandas as pd
import docx
import PyPDF2
from bs4 import BeautifulSoup
from typing import List, Dict, Any

# Initialize logger
logger = logging.getLogger(__name__)

def load_file(file_path: str) -> List[str]:
    """
    Load documents from various file types and return their content as text chunks.

    This function checks the file extension and calls the corresponding method to load and 
    process the file content. Supported file types include text (.txt), markdown (.md), 
    CSV (.csv), Excel (.xlsx), PDF (.pdf), DOCX (.docx), and JSON (.json).

    Args:
        file_path (str): The file path of the document to load.

    Returns:
        List[str]: A list of text chunks representing the document content.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return []

    ext = os.path.splitext(file_path)[1].lower()

    try:
        if ext == '.txt':
            return load_text(file_path)
        elif ext == '.md':
            return load_markdown(file_path)
        elif ext == '.csv':
            return load_csv(file_path)
        elif ext == '.xlsx':
            return load_excel(file_path)
        elif ext == '.pdf':
            return load_pdf(file_path)
        elif ext == '.docx':
            return load_docx(file_path)
        elif ext == '.json':
            return load_json(file_path)
        else:
            logger.warning(f"Unsupported file type: {file_path}")
            return []
    except Exception as e:
        logger.error(f"Error loading file {file_path}: {e}")
        return []


def clean_html_description(description: str) -> str:
    """
    Clean HTML-heavy product descriptions by removing HTML tags and collapsing whitespace.

    This function decodes HTML entities, strips HTML tags using BeautifulSoup, and 
    collapses multiple consecutive whitespace characters into a single space.

    Args:
        description (str): The HTML-heavy description to clean.

    Returns:
        str: The cleaned description with HTML tags removed and whitespace collapsed.
    """
    try:
        decoded = html.unescape(description)
        soup = BeautifulSoup(decoded, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        # Collapse whitespace
        return re.sub(r'\s+', ' ', text)
    except Exception:
        return description


def load_json(file_path: str) -> List[str]:
    """
    Load JSON files and convert to text chunks while cleaning HTML-heavy descriptions.

    This function reads a JSON file, cleans descriptions that may contain HTML, and 
    converts the JSON data into text chunks for further processing.

    Args:
        file_path (str): The file path of the JSON document.

    Returns:
        List[str]: A list of text chunks, each representing a cleaned JSON item.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        chunks = []

        items = data if isinstance(data, list) else [data]
        for item in items:
            if isinstance(item, dict):
                cleaned = item.copy()
                if 'description' in cleaned and isinstance(cleaned['description'], str):
                    cleaned['description'] = clean_html_description(cleaned['description'])
                # Preserve full structure
                chunks.append(json.dumps(cleaned, indent=2, ensure_ascii=False))
            else:
                chunks.append(json.dumps(item, ensure_ascii=False))

        return chunks
    except Exception as e:
        logger.error(f"Error loading JSON: {e}")
        return []


def load_text(file_path: str) -> List[str]:
    """
    Load and chunk text files.

    This function reads a text file, splits its content into paragraphs, and chunks 
    them into smaller pieces, ensuring that each chunk does not exceed a maximum length.

    Args:
        file_path (str): The file path of the text document.

    Returns:
        List[str]: A list of text chunks representing the paragraphs in the file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n', content) if p.strip()]

        chunks, current = [], ''
        for para in paragraphs:
            if len(current) + len(para) < 1000:
                current += para + "\n\n"
            else:
                if current:
                    chunks.append(current.strip())
                current = para + "\n\n"
        if current:
            chunks.append(current.strip())
        return chunks
    except Exception as e:
        logger.error(f"Error loading text file: {e}")
        return []


def load_markdown(file_path: str) -> List[str]:
    """
    Load and chunk markdown files.

    This function reads a markdown file, splits it into sections based on headings, 
    and ensures that the content does not exceed a specified chunk size.

    Args:
        file_path (str): The file path of the markdown document.

    Returns:
        List[str]: A list of text chunks representing the markdown content.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        chunks, current = [], []
        for line in content.split('\n'):
            if line.startswith('#') and current:
                chunks.append('\n'.join(current))
                current = []
            current.append(line)
            if len('\n'.join(current)) > 1000:
                chunks.append('\n'.join(current))
                current = []
        if current:
            chunks.append('\n'.join(current))
        return chunks
    except Exception as e:
        logger.error(f"Error loading markdown: {e}")
        return []


def load_csv(file_path: str) -> List[str]:
    """
    Load CSV files and convert rows to text chunks.

    This function reads a CSV file and converts each row into a text chunk, where each 
    column value is paired with its corresponding column name.

    Args:
        file_path (str): The file path of the CSV document.

    Returns:
        List[str]: A list of text chunks representing the rows in the CSV file.
    """
    try:
        df = pd.read_csv(file_path)
        return [" | ".join(f"{col}: {val}" for col, val in row.items() if pd.notna(val)) for _, row in df.iterrows()]
    except Exception as e:
        logger.error(f"Error loading CSV: {e}")
        return []


def load_excel(file_path: str) -> List[str]:
    """
    Load Excel files and convert rows to text chunks.

    This function reads an Excel file and processes each sheet's rows into text chunks, 
    prefixing each row with the sheet name.

    Args:
        file_path (str): The file path of the Excel document.

    Returns:
        List[str]: A list of text chunks representing the rows in the Excel file.
    """
    try:
        xl = pd.ExcelFile(file_path)
        chunks = []
        for sheet in xl.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet)
            prefix = f"Sheet: {sheet} | "
            for _, row in df.iterrows():
                row_text = prefix + " | ".join(f"{col}: {val}" for col, val in row.items() if pd.notna(val))
                chunks.append(row_text)
        return chunks
    except Exception as e:
        logger.error(f"Error loading Excel: {e}")
        return []


def split_text_to_chunks(text: str, max_length: int = 1000) -> List[str]:
    """
    Split a text into smaller chunks of specified maximum length.

    This function splits the input text into sentences, and then combines them into chunks 
    that do not exceed the specified maximum length.

    Args:
        text (str): The text to split into chunks.
        max_length (int): The maximum length of each chunk (default is 1000).

    Returns:
        List[str]: A list of text chunks.
    """
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    for sentence in sentences:
        if not sentence:
            continue
        if chunks and len(chunks[-1]) + len(sentence) < max_length:
            chunks[-1] += ' ' + sentence
        else:
            chunks.append(sentence)
    return chunks


def process_page_text(index: int, text: str) -> List[str]:
    """
    Process a page's text content and return chunks based on length.

    This function formats the page text by adding a prefix indicating the page number, 
    then splits the text into chunks if necessary.

    Args:
        index (int): The index of the page in the document.
        text (str): The text content of the page.

    Returns:
        List[str]: A list of text chunks for the page.
    """
    if not text.strip():
        return []
    page_text = f"Page {index + 1}: {text}"
    if len(page_text) > 1000:
        return split_text_to_chunks(page_text)
    return [page_text]


def load_pdf(file_path: str) -> List[str]:
    """
    Load and chunk PDF files.

    This function extracts text from each page of a PDF file and splits it into chunks 
    if the text exceeds a specified length.

    Args:
        file_path (str): The file path of the PDF document.

    Returns:
        List[str]: A list of text chunks representing the pages in the PDF.
    """
    try:

        chunks = []
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ''
                chunks.extend(process_page_text(i, text))
        return chunks

    except ImportError:
        logger.error("PyPDF2 not installed. Please install it.")
        return []

    except Exception as e:
        logger.error(f"Error loading PDF: {e}")
        return []


def load_docx(file_path: str) -> List[str]:
    """
    Load and chunk DOCX files.

    This function reads a DOCX file, splits it into paragraphs, and chunks them 
    based on a maximum length to ensure each chunk does not exceed the specified size.

    Args:
        file_path (str): The file path of the DOCX document.

    Returns:
        List[str]: A list of text chunks representing the paragraphs in the DOCX file.
    """
    try:
        doc = docx.Document(file_path)
        paras = [p.text for p in doc.paragraphs if p.text.strip()]
        chunks, current = [], ''
        for para in paras:
            if len(current) + len(para) < 1000:
                current += para + "\n\n"
            else:
                if current:
                    chunks.append(current.strip())
                current = para + "\n\n"
        if current:
            chunks.append(current.strip())
        return chunks
    except ImportError:
        logger.error("python-docx not installed. Please install it.")
        return []
    except Exception as e:
        logger.error(f"Error loading DOCX: {e}")
        return []
