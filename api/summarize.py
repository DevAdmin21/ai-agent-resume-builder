import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status

from application.usecases.summarize import SummarizeTextUseCase
from application.config import Settings, get_settings
from domain.exceptions import (
    DocumentGenerationError,
    LLMEmptySummaryError,
    LLMResponseError,
)
from domain.summary import SummaryRequest, SummaryResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/summarize", tags=["Summarization"])


def get_use_case(settings: Settings = Depends(get_settings)) -> SummarizeTextUseCase:
    """Dependency injection for the use case."""
    return SummarizeTextUseCase(output_dir=Path(settings.output_dir))


@router.post(
    "",
    response_model=SummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Summarize text",
    description=(
        "Receives a text, summarizes it using an AI model, "
        "and optionally generates a downloadable PDF or DOCX document."
    ),
)
async def summarize(
    request: SummaryRequest,
    use_case: SummarizeTextUseCase = Depends(get_use_case),
) -> SummaryResponse:
    """
    POST /api/v1/summarize

    - **text**: The input text to summarize (50–50,000 chars).
    - **generate_document**: Set to true to receive a download URL.
    - **document_format**: "pdf" or "docx" (required if generate_document=true).
    - **language**: ISO 639-1 language code for the summary output (default "es").
    """
    logger.info(
        "Summarization request | text_length=%d | generate_document=%s | format=%s",
        len(request.text),
        request.generate_document,
        request.document_format,
    )

    try:
        return await use_case.execute(request)

    except (LLMResponseError, LLMEmptySummaryError) as exc:
        logger.warning("LLM error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI model error: {exc}",
        ) from exc

    except DocumentGenerationError as exc:
        logger.error("Document generation error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document generation failed: {exc}",
        ) from exc

    except Exception as exc:
        logger.exception("Unexpected error during summarization")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again.",
        ) from exc