from enum import Enum
from pydantic import BaseModel, Field, field_validator


class DocumentFormat(str, Enum):
    PDF = "pdf"
    DOCX = "docx"


class SummaryRequest(BaseModel):
    """Input request validated at domain level."""

    text: str = Field(
        ...,
        min_length=50,
        max_length=50_000,
        description="Text to summarize (50 to 50,000 characters).",
    )
    generate_document: bool = Field(
        default=False,
        description="If True, generates a downloadable document.",
    )
    document_format: DocumentFormat | None = Field(
        default=None,
        description="Document format: 'pdf' or 'docx'. Required when generate_document=True.",
    )
    language: str = Field(
        default="es",
        pattern="^[a-z]{2}$",
        description="Output language ISO 639-1 code (e.g. 'es', 'en').",
    )

    @field_validator("document_format")
    @classmethod
    def validate_document_format(
        cls, v: DocumentFormat | None, info
    ) -> DocumentFormat | None:
        if info.data.get("generate_document") and v is None:
            raise ValueError(
                "document_format is required when generate_document is True."
            )
        return v

    @field_validator("text")
    @classmethod
    def validate_text_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Text must not be empty or whitespace only.")
        return stripped


class SummaryResult(BaseModel):
    """Validated output from LLM."""

    summary: str = Field(..., description="The generated summary.")
    key_points: list[str] = Field(
        default_factory=list,
        description="Key bullet points extracted from the text.",
    )
    word_count_original: int = Field(..., description="Word count of original text.")
    word_count_summary: int = Field(..., description="Word count of summary.")


class SummaryResponse(BaseModel):
    """Final API response."""

    summary: str
    key_points: list[str]
    word_count_original: int
    word_count_summary: int
    document_url: str | None = Field(
        default=None,
        description="URL to download the document, if requested.",
    )