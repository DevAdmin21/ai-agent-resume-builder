import logging
from pathlib import Path

from domain.summary import SummaryRequest, SummaryResponse
from infrastructure.document_generators import generate_document
from infrastructure.llm.summarizer_chain import summarize_text

logger = logging.getLogger(__name__)


class SummarizeTextUseCase:
    """
    Orchestrates the full summarization flow:
      1. Call LLM to produce a validated SummaryResult.
      2. Optionally generate a document.
      3. Return a SummaryResponse.

    No business logic lives here beyond orchestration.
    """

    def __init__(self, output_dir: Path) -> None:
        self._output_dir = output_dir

    async def execute(self, request: SummaryRequest) -> SummaryResponse:
        # Step 1 — Summarize via LLM
        logger.info("Starting summarization use case")
        result = await summarize_text(request.text, request.language)

        # Step 2 — Optionally generate document
        document_url: str | None = None
        if request.generate_document and request.document_format:
            file_path = generate_document(
                result, request.document_format, self._output_dir
            )
            document_url = f"/files/{file_path.name}"
            logger.info("Document generated: %s", document_url)

        return SummaryResponse(
            summary=result.summary,
            key_points=result.key_points,
            word_count_original=result.word_count_original,
            word_count_summary=result.word_count_summary,
            document_url=document_url,
        )