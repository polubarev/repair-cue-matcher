"""
Text normalization utilities.

Pipeline:
- Unicode NFC normalization.
- Case-folding (case-insensitive).
- Accent stripping (accent-insensitive).
- Light punctuation canonicalization (e.g., curly quotes to ASCII).
- Whitespace collapsing.
"""

from __future__ import annotations

import re
import unicodedata


_WHITESPACE_RE = re.compile(r"\s+")


def _strip_accents(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")


def normalize(text: str) -> str:
    """
    Normalize text for robust cue matching.

    - NFC normalize.
    - Case-fold.
    - Strip accents.
    - Canonicalize common punctuation.
    - Collapse internal whitespace.
    """

    if not isinstance(text, str):
        text = str(text)

    # NFC normalization and case-folding
    text = unicodedata.normalize("NFC", text)
    text = text.casefold()

    # Canonicalize common punctuation (curly quotes, etc.)
    punctuation_map = {
        "’": "'",
        "‘": "'",
        "“": '"',
        "”": '"',
        "―": "-",
        "–": "-",
        "—": "-",
    }
    for src, tgt in punctuation_map.items():
        text = text.replace(src, tgt)

    # Accent-insensitive: strip combining marks
    text = _strip_accents(text)
    text = unicodedata.normalize("NFC", text)

    # Collapse whitespace
    text = _WHITESPACE_RE.sub(" ", text).strip()

    return text

