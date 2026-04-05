from pathlib import Path

from domain.summary import DocumentFormat, SummaryResult
from infrastructure.document_generators.docx_generator import generate_docx
from infrastructure.document_generators.pdf_generator import generate_pdf


def generate_document(
    result: SummaryResult,
    fmt: DocumentFormat,
    output_dir: Path,
) -> Path:
    """Dispatch document generation to the correct generator."""
    if fmt == DocumentFormat.PDF:
        return generate_pdf(result, output_dir)
    if fmt == DocumentFormat.DOCX:
        return generate_docx(result, output_dir)
    raise ValueError(f"Unsupported document format: {fmt}")