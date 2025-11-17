"""
Utilities for loading and preparing repair-cue patterns.

Expected cue file format (INI-like):

    [ASK_TO_REPEAT]
    can you repeat
    say that again

    [REPHRASE]
    let me rephrase
    in other words

Blank lines are ignored.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from .normalization import normalize
from .models import CuePattern


@dataclass
class RawCue:
    category: str
    phrase: str


def load_raw_cues(path: str | Path) -> List[RawCue]:
    """Load raw cues from an INI-like file."""

    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Cue file not found: {p}")

    raw_cues: List[RawCue] = []
    current_category: str | None = None

    with p.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            if line.startswith("[") and line.endswith("]"):
                current_category = line[1:-1].strip()
                continue

            if current_category is None:
                # Skip lines before the first category header.
                continue

            raw_cues.append(RawCue(category=current_category, phrase=line))

    return raw_cues


def build_cue_patterns(raw_cues: Iterable[RawCue]) -> List[CuePattern]:
    """Convert raw cues into normalized CuePattern objects."""

    patterns: List[CuePattern] = []
    for idx, cue in enumerate(raw_cues):
        normalized = normalize(cue.phrase)
        patterns.append(
            CuePattern(
                id=idx,
                category=cue.category,
                raw_phrase=cue.phrase,
                normalized_phrase=normalized,
            )
        )
    return patterns


def expand_to_k(patterns: List[CuePattern], k: int) -> List[CuePattern]:
    """
    Ensure we have at least k patterns.

    If there are fewer than k unique cues, generate synthetic variants by
    appending polite suffixes or small clarifications. This is acceptable
    for benchmarking because we care about runtime scaling with k, not
    semantic distinctness of each cue.
    """

    if k <= 0:
        return []

    if len(patterns) >= k:
        base = patterns[:k]
    else:
        base = list(patterns)

    # Generate synthetic variants if needed.
    suffixes = [
        " please",
        " please.",
        " again",
        " one more time",
        " por favor",
        " de nuevo",
    ]

    augmented: List[CuePattern] = list(base)
    idx = 0
    while len(augmented) < k and patterns:
        original = patterns[idx % len(patterns)]
        suffix = suffixes[(idx // len(patterns)) % len(suffixes)]
        new_raw = f"{original.raw_phrase}{suffix}"
        new_norm = normalize(new_raw)
        augmented.append(
            CuePattern(
                id=len(augmented),
                category=original.category,
                raw_phrase=new_raw,
                normalized_phrase=new_norm,
            )
        )
        idx += 1

    # Reassign ids to keep them dense 0..k-1.
    final_patterns: List[CuePattern] = []
    for new_id, p in enumerate(augmented[:k]):
        final_patterns.append(
            CuePattern(
                id=new_id,
                category=p.category,
                raw_phrase=p.raw_phrase,
                normalized_phrase=p.normalized_phrase,
            )
        )

    return final_patterns
