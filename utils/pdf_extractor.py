"""
pdf_extractor.py
----------------
Extracts plain text from uploaded PDF resumes.
Uses PyMuPDF (fitz) as the primary parser for accurate text extraction,
with pdfplumber as a fallback for complex layouts.
"""

import io
import streamlit as st

# Try PyMuPDF first; fall back to pdfplumber
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False


def extract_text_from_pdf(uploaded_file) -> str:
    """
    Extract all readable text from a Streamlit-uploaded PDF file.

    Strategy:
    1. Try PyMuPDF (fastest, best for most resumes).
    2. Fall back to pdfplumber (better for table-heavy layouts).
    3. Return empty string if both fail.

    Args:
        uploaded_file: Streamlit UploadedFile object.

    Returns:
        Extracted text as a single string, pages separated by newlines.
    """
    raw_bytes = uploaded_file.read()

    # ── Primary: PyMuPDF ──────────────────────────────────────────────────
    if PYMUPDF_AVAILABLE:
        try:
            text = _extract_with_pymupdf(raw_bytes)
            if text and len(text.strip()) > 50:
                return text
        except Exception as e:
            st.warning(f"PyMuPDF extraction issue ({e}); trying fallback…")

    # ── Fallback: pdfplumber ──────────────────────────────────────────────
    if PDFPLUMBER_AVAILABLE:
        try:
            text = _extract_with_pdfplumber(raw_bytes)
            if text and len(text.strip()) > 50:
                return text
        except Exception as e:
            st.warning(f"pdfplumber extraction issue ({e}).")

    return ""


def _extract_with_pymupdf(raw_bytes: bytes) -> str:
    """Use PyMuPDF to extract text, preserving paragraph structure."""
    doc = fitz.open(stream=raw_bytes, filetype="pdf")
    pages = []
    for page in doc:
        # "text" mode gives clean paragraphs; "blocks" gives layout-aware blocks
        pages.append(page.get_text("text"))
    doc.close()
    return "\n\n".join(pages)


def _extract_with_pdfplumber(raw_bytes: bytes) -> str:
    """Use pdfplumber for more robust extraction of tabular content."""
    with pdfplumber.open(io.BytesIO(raw_bytes)) as pdf:
        pages = []
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return "\n\n".join(pages)


def clean_resume_text(raw_text: str) -> str:
    """
    Light post-processing to fix common PDF extraction artefacts.
    - Collapses excessive blank lines.
    - Removes non-printable control characters.
    - Strips leading/trailing whitespace per line.
    """
    import re
    # Remove control characters (keep newlines and tabs)
    text = re.sub(r"[^\S\n\t ]+", " ", raw_text)
    # Collapse 3+ consecutive newlines to two
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip trailing spaces on each line
    lines = [line.rstrip() for line in text.splitlines()]
    return "\n".join(lines).strip()
