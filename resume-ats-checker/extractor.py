# extractor.py
# Extracts text from uploaded PDF or DOCX resume

import fitz  # PyMuPDF
from docx import Document
import os

def extract_text_from_pdf(filepath):
    """Extract all text from a PDF file"""
    text = ""
    try:
        doc = fitz.open(filepath)
        for page in doc:
            text += page.get_text()
        doc.close()
    except Exception as e:
        print(f"PDF extraction error: {e}")
    return text.lower().strip()

def extract_text_from_docx(filepath):
    """Extract all text from a DOCX file"""
    text = ""
    try:
        doc = Document(filepath)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"DOCX extraction error: {e}")
    return text.lower().strip()

def extract_text(filepath):
    """Auto detect file type and extract text"""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(filepath)
    elif ext == ".docx":
        return extract_text_from_docx(filepath)
    else:
        return ""