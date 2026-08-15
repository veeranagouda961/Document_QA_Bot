from pathlib import Path

from pypdf import PdfReader


def extract_text_from_pdf(pdf_path):
    """Extract text from all pages of a PDF document."""

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF file not found: {pdf_path}"
        )

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(
            "Only PDF files are supported."
        )

    reader = PdfReader(str(pdf_path))

    extracted_text = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text()

        if page_text:
            extracted_text.append(page_text)

    if not extracted_text:
        raise ValueError(
            "No readable text was found in the PDF."
        )

    return "\n".join(extracted_text)


def split_into_chunks(text, chunk_size=1500, overlap=200):
    """Split document text into overlapping chunks."""

    if not text.strip():
        raise ValueError("Cannot create chunks from empty text.")

    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "Overlap must be non-negative and smaller than chunk size."
        )

    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start = end - overlap

    return chunks