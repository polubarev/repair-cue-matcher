"""
Transcript parsing and integration logic.

Key integration rule:
- Run repair-cue detection only on AGENT turns that immediately follow
  a PATIENT turn (“fire only after patient turn”).
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Tuple

from .types import Conversation, Turn


def parse_transcripts(path: str | Path) -> List[Conversation]:
    """
    Parse transcripts in the provided assignment format.

    Format:
        ===== Transcript 1 =====
        AGENT: ...
        PATIENT: ...

    Blank lines between conversations are allowed.
    """

    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Transcripts file not found: {p}")

    conversations: List[Conversation] = []
    current_turns: List[Turn] = []
    current_conv_id: str | None = None

    with p.open(encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue

            if stripped.startswith("===== Transcript") and stripped.endswith("====="):
                # Start of a new conversation.
                if current_conv_id is not None:
                    conversations.append(
                        Conversation(conv_id=current_conv_id, turns=list(current_turns))
                    )
                    current_turns.clear()

                # Extract numeric ID or use the whole header as identifier.
                parts = stripped.strip("=").strip().split()
                conv_id = parts[-1] if parts else stripped
                current_conv_id = str(conv_id)
                continue

            # Turn lines: "AGENT: ..." or "PATIENT: ..."
            if ":" in stripped:
                speaker, text = stripped.split(":", 1)
                speaker = speaker.strip().upper()
                text = text.strip()
                if speaker in {"AGENT", "PATIENT"}:
                    current_turns.append(Turn(speaker=speaker, text=text))

    # Flush last conversation
    if current_conv_id is not None:
        conversations.append(
            Conversation(conv_id=current_conv_id, turns=list(current_turns))
        )

    return conversations


def agent_turns_after_patient(
    conversations: Iterable[Conversation],
) -> List[Tuple[Conversation, int]]:
    """
    Return (conversation, turn_index) pairs where:
    - turn is an AGENT turn
    - immediately preceded by a PATIENT turn.
    """

    result: List[Tuple[Conversation, int]] = []
    for conv in conversations:
        for idx in range(1, len(conv.turns)):
            prev_turn = conv.turns[idx - 1]
            turn = conv.turns[idx]
            if prev_turn.speaker == "PATIENT" and turn.speaker == "AGENT":
                result.append((conv, idx))
    return result

