import json
import logging
from dotenv import load_dotenv
from functools import lru_cache

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from application.config import get_settings
from domain.exceptions import LLMEmptySummaryError, LLMResponseError
from domain.summary import SummaryResult

load_dotenv()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prompt Template
# ---------------------------------------------------------------------------
# Design principles:
#   1. Role assignment → reduces hallucination, anchors behavior
#   2. Explicit JSON schema → forces structured output
#   3. Negative constraints → avoids padding or invented content
#   4. Language awareness → handles multilingual input/output cleanly
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are an expert summarization assistant. Your role is to produce accurate, \
concise, and faithful summaries of the provided text.

RULES (follow strictly):
- Preserve all critical facts, names, dates, and figures from the original text.
- Do NOT invent, infer, or add information not present in the original.
- Do NOT include generic phrases like "In conclusion" or "As mentioned above".
- The summary must be written in the language specified by the user.
- Key points must be concrete, standalone sentences — not vague bullet headers.

OUTPUT FORMAT — respond ONLY with valid JSON, no extra text, no markdown fences:
{{
  "summary": "<concise summary paragraph(s)>",
  "key_points": ["<point 1>", "<point 2>", "<point 3>"]
}}
"""

HUMAN_PROMPT = """\
Summarize the following text in {language}.

TEXT:
{text}

Remember: respond only with the JSON object described in your instructions.
"""


def _build_chain():
    settings = get_settings()

    llm = ChatOpenAI(
        model=settings.openai_model,
        temperature=settings.openai_temperature,
        max_tokens=settings.openai_max_tokens,
        api_key=settings.openai_api_key,
        # Retry transient errors automatically
        max_retries=2,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", HUMAN_PROMPT),
        ]
    )

    return prompt | llm | StrOutputParser()


@lru_cache(maxsize=1)
def get_summarizer_chain():
    """Singleton chain — built once, reused across requests."""
    return _build_chain()


# ---------------------------------------------------------------------------
# Response validation
# ---------------------------------------------------------------------------

def _parse_llm_output(raw: str, original_text: str) -> SummaryResult:
    """
    Parse and validate LLM JSON output.
    Raises LLMResponseError or LLMEmptySummaryError on bad output.
    """
    # Strip accidental markdown fences the model might add despite instructions
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        cleaned = "\n".join(
            line for line in lines if not line.startswith("```")
        ).strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        logger.error("LLM returned non-JSON output: %s", raw[:500])
        raise LLMResponseError(
            f"LLM response is not valid JSON. Raw output: {raw[:200]}"
        ) from exc

    summary: str = data.get("summary", "").strip()
    key_points: list = data.get("key_points", [])

    if not summary:
        raise LLMEmptySummaryError("LLM returned an empty summary.")

    if len(summary) < 20:
        raise LLMEmptySummaryError(
            f"LLM summary is suspiciously short ({len(summary)} chars)."
        )

    if not isinstance(key_points, list):
        logger.warning("key_points is not a list — defaulting to empty.")
        key_points = []

    # Sanitize key_points: keep only non-empty strings
    key_points = [str(kp).strip() for kp in key_points if str(kp).strip()]

    return SummaryResult(
        summary=summary,
        key_points=key_points,
        word_count_original=len(original_text.split()),
        word_count_summary=len(summary.split()),
    )


async def summarize_text(text: str, language: str = "es") -> SummaryResult:
    """
    Invoke the LLM chain and return a validated SummaryResult.
    """
    chain = get_summarizer_chain()

    logger.info(
        "Invoking LLM summarization | words=%d | language=%s",
        len(text.split()),
        language,
    )

    try:
        raw_output: str = await chain.ainvoke({"text": text, "language": language})
    except Exception as exc:
        logger.exception("LLM chain invocation failed")
        raise LLMResponseError(f"LLM call failed: {exc}") from exc

    result = _parse_llm_output(raw_output, text)

    logger.info(
        "Summarization complete | original_words=%d | summary_words=%d",
        result.word_count_original,
        result.word_count_summary,
    )

    return result