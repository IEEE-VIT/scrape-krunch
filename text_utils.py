"""Utilities for cleaning scraped article text before caching or LLM use."""

import re
import unicodedata


_WHITESPACE_RE = re.compile(r"[\t\n\r\f\v]+")
_MULTI_SPACE_RE = re.compile(r" {2,}")


def clean_extracted_text(text):
    """Normalize scraped article text.

    BeautifulSoup often leaves non-breaking spaces (\\xa0), runs of newlines,
    and trailing tabs. Collapse those artifacts so prompts sent to Ollama
    stay compact and readable.
    """
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)

    normalized = []
    for ch in text:
        if ch == "\xa0" or unicodedata.category(ch) == "Zs":
            normalized.append(" ")
        else:
            normalized.append(ch)
    text = "".join(normalized)

    text = _WHITESPACE_RE.sub(" ", text)
    text = _MULTI_SPACE_RE.sub(" ", text)
    return text.strip()
