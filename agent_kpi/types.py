from dataclasses import dataclass
from typing import List


@dataclass
class CuePattern:
    """Represents a single repair-cue pattern."""

    id: int
    category: str
    raw_phrase: str
    normalized_phrase: str


@dataclass
class Match:
    """Single match of a repair cue inside a turn."""

    pattern: CuePattern
    start: int
    end: int


@dataclass
class Turn:
    """One conversational turn."""

    speaker: str  # e.g. "AGENT" or "PATIENT"
    text: str


@dataclass
class Conversation:
    """A full conversation consisting of ordered turns."""

    conv_id: str
    turns: List[Turn]

