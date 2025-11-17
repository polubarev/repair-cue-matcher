"""
Aho–Corasick multi-pattern matcher for repair cues.

Per-turn runtime is O(L + M), where:
- L = length of the normalized turn.
- M = number of matches.

This complexity is independent of the number of patterns k
after the automaton is constructed.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Dict, List

from .normalization import normalize
from .types import CuePattern, Match


@dataclass
class _Node:
    children: Dict[str, int]
    fail: int
    outputs: List[int]


class AhoCorasickMatcher:
    """Aho–Corasick automaton over normalized cue patterns."""

    def __init__(self, patterns: List[CuePattern]) -> None:
        self.patterns = patterns
        self._nodes: List[_Node] = []
        self._build_trie()
        self._build_failure_links()

    def _new_node(self) -> int:
        self._nodes.append(_Node(children={}, fail=0, outputs=[]))
        return len(self._nodes) - 1

    def _build_trie(self) -> None:
        self._new_node()  # root at index 0

        for pattern in self.patterns:
            current = 0
            for ch in pattern.normalized_phrase:
                if ch not in self._nodes[current].children:
                    self._nodes[current].children[ch] = self._new_node()
                current = self._nodes[current].children[ch]
            self._nodes[current].outputs.append(pattern.id)

    def _build_failure_links(self) -> None:
        queue: deque[int] = deque()

        # Initialize depth-1 nodes
        for ch, child in self._nodes[0].children.items():
            self._nodes[child].fail = 0
            queue.append(child)

        # BFS
        while queue:
            state = queue.popleft()

            for ch, child in self._nodes[state].children.items():
                queue.append(child)

                # Follow failure links for the next state
                fail_state = self._nodes[state].fail
                while fail_state and ch not in self._nodes[fail_state].children:
                    fail_state = self._nodes[fail_state].fail

                self._nodes[child].fail = self._nodes[fail_state].children.get(ch, 0)

                # Merge outputs from failure state
                self._nodes[child].outputs.extend(
                    self._nodes[self._nodes[child].fail].outputs
                )

    def find_all(self, text: str) -> List[Match]:
        """
        Find all cue matches in the given text.

        The text is normalized internally, so callers can pass raw turns.
        """

        normalized = normalize(text)
        results: List[Match] = []

        state = 0
        for idx, ch in enumerate(normalized):
            # Follow failure links until we can transition on ch
            while state and ch not in self._nodes[state].children:
                state = self._nodes[state].fail

            state = self._nodes[state].children.get(ch, 0)

            if self._nodes[state].outputs:
                for pattern_id in self._nodes[state].outputs:
                    pattern = self.patterns[pattern_id]
                    length = len(pattern.normalized_phrase)
                    end = idx + 1
                    start = end - length
                    results.append(Match(pattern=pattern, start=start, end=end))

        return results

