import logging
import uuid
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

from domain.exceptions import DocumentGenerationError
from domain.summary import SummaryResult

logger = logging.getLogger(__name__)


def generate_pdf(result: SummaryResult, output_dir: Path) -> Path:
    """
    Generate a styled PDF from a SummaryResult.
    Returns the path to the generated file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / f"summary_{uuid.uuid4().hex[:8]}.pdf"

    try:
        _build_pdf(result, file_path)
    except Exception as exc:
        logger.exception("PDF generation failed")
        raise DocumentGenerationError(f"Failed to generate PDF: {exc}") from exc

    logger.info("PDF generated at %s", file_path)
    return file_path


def _build_pdf(result: SummaryResult, file_path: Path) -> None:
    doc = SimpleDocTemplate(
        str(file_path),
        pagesize=letter,
        leftMargin=inch,
        rightMargin=inch,
        topMargin=inch,
        bottomMargin=inch,
    )

    styles = getSampleStyleSheet()
    story = []

    # ── Title ──────────────────────────────────────────────────────────────
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=20,
        spaceAfter=16,
        textColor="#1a1a2e",
    )
    story.append(Paragraph("Document Summary", title_style))
    story.append(Spacer(1, 0.1 * inch))

    # ── Metadata bar ───────────────────────────────────────────────────────
    meta_style = ParagraphStyle(
        "Meta",
        parent=styles["Normal"],
        fontSize=9,
        textColor="#666666",
        spaceAfter=20,
    )
    story.append(
        Paragraph(
            f"Original: <b>{result.word_count_original} words</b> &nbsp;|&nbsp; "
            f"Summary: <b>{result.word_count_summary} words</b> &nbsp;|&nbsp; "
            f"Reduction: <b>{_reduction_pct(result)}%</b>",
            meta_style,
        )
    )

    # ── Summary Section ────────────────────────────────────────────────────
    section_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=13,
        textColor="#16213e",
        spaceBefore=12,
        spaceAfter=8,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=11,
        leading=17,
        spaceAfter=12,
    )

    story.append(Paragraph("Summary", section_style))
    story.append(Paragraph(result.summary, body_style))

    # ── Key Points Section ─────────────────────────────────────────────────
    if result.key_points:
        story.append(Spacer(1, 0.15 * inch))
        story.append(Paragraph("Key Points", section_style))

        bullet_style = ParagraphStyle(
            "Bullet",
            parent=styles["Normal"],
            fontSize=11,
            leading=16,
        )
        items = [
            ListItem(Paragraph(point, bullet_style), bulletColor="#0f3460")
            for point in result.key_points
        ]
        story.append(ListFlowable(items, bulletType="bullet", leftIndent=20))

    doc.build(story)


def _reduction_pct(result: SummaryResult) -> int:
    if result.word_count_original == 0:
        return 0
    return round(
        (1 - result.word_count_summary / result.word_count_original) * 100
    )