"""
Naive k-regex baseline matcher.

This implementation compiles one regex per cue pattern and runs them
independently over each turn, leading to O(k * L) runtime per turn.
"""

from __future__ import annotations

import re
from typing import List

from .normalization import normalize
from .types import CuePattern, Match


class RegexBaselineMatcher:
    """Naive baseline that uses one regex per cue pattern."""

    def __init__(self, patterns: List[CuePattern]) -> None:
        self.patterns = patterns
        self._compiled = []
        for pattern in patterns:
            # Use the normalized phrase as the literal pattern.
            escaped = re.escape(pattern.normalized_phrase)
            self._compiled.append((pattern, re.compile(escaped)))

    def find_all(self, text: str) -> List[Match]:
        """
        Run k independent regexes against the normalized text.
        """

        normalized = normalize(text)
        results: List[Match] = []

        for pattern, regex in self._compiled:
            for m in regex.finditer(normalized):
                results.append(
                    Match(
                        pattern=pattern,
                        start=m.start(),
                        end=m.end(),
                    )
                )

        return results

