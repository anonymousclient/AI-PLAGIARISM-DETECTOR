import os
import re
from PyPDF2 import PdfReader
from docx import Document


def extract_text(file_path):
    """Extract text from PDF or DOCX file."""
    try:
        extension = os.path.splitext(file_path)[1].lower()

        if extension == ".pdf":
            return extract_from_pdf(file_path)
        elif extension == ".docx":
            return extract_from_docx(file_path)
        else:
            return ""
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""


def extract_from_pdf(file_path):
    """Read all pages from a PDF and combine text."""
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + " "
    return clean_text(text)


def extract_from_docx(file_path):
    """Read all paragraphs from a DOCX and combine text."""
    doc = Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + " "
    return clean_text(text)


def clean_text(text):
    """Clean extracted text: lowercase, remove special chars, collapse spaces."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
