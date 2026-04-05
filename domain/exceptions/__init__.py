class SummarizerError(Exception):
    """Base exception for the summarizer service."""


class LLMResponseError(SummarizerError):
    """Raised when the LLM returns an invalid or unparseable response."""


class LLMEmptySummaryError(SummarizerError):
    """Raised when LLM summary is empty or too short."""


class DocumentGenerationError(SummarizerError):
    """Raised when document generation fails."""


class TextValidationError(SummarizerError):
    """Raised when input text fails domain validation."""