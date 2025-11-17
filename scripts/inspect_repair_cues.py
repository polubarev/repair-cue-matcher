"""
Inspect detected repair cues in the sample transcripts.

This script:
- Parses conversations from the assignment transcripts.
- Applies the "fire only after patient turn" rule.
- Runs the Aho–Corasick matcher on eligible agent turns.
- Prints all detected cues with their categories.
"""

from __future__ import annotations

from pathlib import Path
import sys


# Ensure project root is on sys.path so `agent_kpi` is importable
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent_kpi.aho_matcher import AhoCorasickMatcher
from agent_kpi.integration import agent_turns_after_patient, parse_transcripts
from agent_kpi.patterns import build_cue_patterns, load_raw_cues


def main() -> None:
    transcripts_path = Path(
        "AI engineer assignment/AI engineer assignment transcripts.txt"
    )
    cues_path = Path("solution/repair_cues.txt")

    conversations = parse_transcripts(transcripts_path)
    pairs = agent_turns_after_patient(conversations)

    patterns = build_cue_patterns(load_raw_cues(cues_path))
    matcher = AhoCorasickMatcher(patterns)

    for conv, idx in pairs:
        turn = conv.turns[idx]
        matches = matcher.find_all(turn.text)
        if matches:
            print(f"Conversation {conv.conv_id}, AGENT turn {idx}: {turn.text}")
            for m in matches:
                print(f"  - [{m.pattern.category}] {m.pattern.raw_phrase}")
            print()


if __name__ == "__main__":
    main()
