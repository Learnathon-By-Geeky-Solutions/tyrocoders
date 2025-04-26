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

def load_file(file_path: str) -> List[str]:
    """Load documents from various file types"""
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
    """Clean HTML-heavy product descriptions"""
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
    Load JSON files and convert to text chunks while cleaning HTML-heavy descriptions
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
    Load and chunk text files
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
    Load and chunk markdown files
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
    Load CSV files and convert rows to text chunks
    """
    try:
        df = pd.read_csv(file_path)
        return [" | ".join(f"{col}: {val}" for col, val in row.items() if pd.notna(val)) for _, row in df.iterrows()]
    except Exception as e:
        logger.error(f"Error loading CSV: {e}")
        return []


def load_excel(file_path: str) -> List[str]:
    """
    Load Excel files and convert rows to text chunks
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
    if not text.strip():
        return []
    page_text = f"Page {index + 1}: {text}"
    if len(page_text) > 1000:
        return split_text_to_chunks(page_text)
    return [page_text]

def load_pdf(file_path: str) -> List[str]:
    """
    Load and chunk PDF files
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
    Load and chunk DOCX files
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


# import os
# import re
# import json
# import html
# from typing import List
# from pathlib import Path
# import warnings
# from functools import lru_cache

# from core.logger import logger

# # Suppress warnings
# warnings.filterwarnings("ignore")

# def lazy_import_pandas():
#     """Lazy import pandas to reduce startup time"""
#     import pandas as pd
#     return pd

# def load_file(file_path: str) -> List[str]:
#     """Router function with lazy extensions"""
#     ext = os.path.splitext(file_path)[1].lower()
#     try:
#         if ext == '.json':
#             return load_json(file_path)
#         elif ext == '.txt':
#             return load_text(file_path)
#         elif ext == '.md':
#             return load_markdown(file_path)
#         elif ext == '.csv':
#             return load_csv(file_path)
#         elif ext == '.xlsx':
#             return load_excel(file_path)
#         elif ext == '.pdf':
#             return load_pdf(file_path)
#         elif ext == '.docx':
#             return load_docx(file_path)
#         else:
#             return []
#     except Exception as e:
#         logger.error(f"Error loading {file_path}: {e}")
#         return []

# def load_json(file_path: str) -> List[str]:
#     """Optimized JSON loader"""
#     try:
#         with open(file_path, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#         return [json.dumps(item, ensure_ascii=False) for item in (data if isinstance(data, list) else [data])]
#     except Exception as e:
#         logger.error(f"JSON load error: {e}")
#         return []

# def load_csv(file_path: str) -> List[str]:
#     """Lazy pandas CSV loader"""
#     try:
#         pd = lazy_import_pandas()
#         df = pd.read_csv(file_path)
#         return [
#             " | ".join(f"{col}: {val}" 
#             for col, val in row.items() 
#             if pd.notna(val))
#             for _, row in df.iterrows()
#         ]
#     except Exception as e:
#         logger.error(f"CSV load error: {e}")
#         return []

# def load_excel(file_path: str) -> List[str]:
#     """Lazy Excel loader"""
#     try:
#         pd = lazy_import_pandas()
#         xl = pd.ExcelFile(file_path)
#         chunks = []
#         for sheet in xl.sheet_names:
#             df = pd.read_excel(file_path, sheet_name=sheet)
#             prefix = f"Sheet: {sheet} | "
#             chunks.extend(
#                 prefix + " | ".join(f"{col}: {val}" for col, val in row.items() if pd.notna(val))
#                 for _, row in df.iterrows()
#             )
#         return chunks
#     except Exception as e:
#         logger.error(f"Excel load error: {e}")
#         return []

# def load_pdf(file_path: str) -> List[str]:
#     """Lazy PDF loader"""
#     try:
#         import PyPDF2
#         chunks = []
#         with open(file_path, 'rb') as f:
#             reader = PyPDF2.PdfReader(f)
#             for i, page in enumerate(reader.pages):
#                 if text := (page.extract_text() or '').strip():
#                     chunks.append(f"Page {i+1}: {text}")
#         return chunks
#     except ImportError:
#         logger.error("PyPDF2 not installed")
#         return []
#     except Exception as e:
#         logger.error(f"PDF load error: {e}")
#         return []

# def load_text(file_path: str) -> List[str]:
#     """Optimized text file loader with chunking"""
#     try:
#         with open(file_path, 'r', encoding='utf-8') as f:
#             content = f.read()
        
#         # Improved paragraph splitting with whitespace handling
#         paragraphs = [
#             p.strip() for p in 
#             re.split(r'\n\s*\n', content) 
#             if p.strip()
#         ]
        
#         chunks = []
#         current_chunk = []
#         current_length = 0
        
#         for para in paragraphs:
#             para_length = len(para)
#             if current_length + para_length < 1000:
#                 current_chunk.append(para)
#                 current_length += para_length
#             else:
#                 if current_chunk:
#                     chunks.append("\n\n".join(current_chunk))
#                 current_chunk = [para]
#                 current_length = para_length
        
#         if current_chunk:
#             chunks.append("\n\n".join(current_chunk))
            
#         return chunks
        
#     except Exception as e:
#         logger.error(f"Text load error: {e}")
#         return []

# def load_markdown(file_path: str) -> List[str]:
#     """Optimized Markdown loader with section-aware chunking"""
#     try:
#         with open(file_path, 'r', encoding='utf-8') as f:
#             content = f.read()
        
#         chunks = []
#         current_chunk = []
#         in_code_block = False
        
#         for line in content.split('\n'):
#             # Handle code blocks
#             if line.strip().startswith('```'):
#                 in_code_block = not in_code_block
            
#             # Section break detection
#             if line.startswith('#') and not in_code_block and current_chunk:
#                 chunks.append("\n".join(current_chunk))
#                 current_chunk = []
            
#             current_chunk.append(line)
            
#             # Flush if chunk gets too large
#             if len("\n".join(current_chunk)) > 1000:
#                 chunks.append("\n".join(current_chunk))
#                 current_chunk = []
        
#         if current_chunk:
#             chunks.append("\n".join(current_chunk))
            
#         return chunks
        
#     except Exception as e:
#         logger.error(f"Markdown load error: {e}")
#         return []

# def load_docx(file_path: str) -> List[str]:
#     """Optimized DOCX loader with paragraph handling"""
#     try:
#         import docx
#         doc = docx.Document(file_path)
        
#         chunks = []
#         current_chunk = []
#         current_length = 0
        
#         for para in doc.paragraphs:
#             text = para.text.strip()
#             if not text:
#                 continue
                
#             text_length = len(text)
#             if current_length + text_length < 1000:
#                 current_chunk.append(text)
#                 current_length += text_length
#             else:
#                 if current_chunk:
#                     chunks.append("\n\n".join(current_chunk))
#                 current_chunk = [text]
#                 current_length = text_length
        
#         if current_chunk:
#             chunks.append("\n\n".join(current_chunk))
            
#         return chunks
        
#     except ImportError:
#         logger.error("python-docx not installed")
#         return []
#     except Exception as e:
#         logger.error(f"DOCX load error: {e}")
#         return []

# def clean_html_description(description: str) -> str:
#     """Optimized HTML cleaner with BeautifulSoup"""
#     try:
#         from bs4 import BeautifulSoup
#         decoded = html.unescape(description)
#         soup = BeautifulSoup(decoded, "html.parser")
        
#         # Remove unwanted elements
#         for element in soup(['script', 'style', 'iframe', 'noscript']):
#             element.decompose()
            
#         # Get text with improved spacing
#         text = soup.get_text(separator=" ", strip=True)
        
#         # Advanced whitespace cleanup
#         text = re.sub(r'\s+', ' ', text)  # Collapse multiple spaces
#         text = re.sub(r'\s([.,!?;:])', r'\1', text)  # Fix punctuation spacing
#         return text
        
#     except Exception:
#         # Fallback to simple cleaning
#         return re.sub(r'<[^>]+>', '', html.unescape(description))