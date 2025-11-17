"""
Micro-benchmark for repair-cue matchers.

Compares Aho–Corasick vs naive k-regex baseline at k ∈ {10, 50, 200}
using the provided transcripts and cue list.
"""

from __future__ import annotations

import argparse
import statistics
import time
from pathlib import Path
from typing import Iterable, List, Sequence

from .aho_matcher import AhoCorasickMatcher
from .integration import agent_turns_after_patient, parse_transcripts
from .patterns import build_cue_patterns, expand_to_k, load_raw_cues
from .regex_baseline import RegexBaselineMatcher


def _benchmark_matcher(
    matcher, texts: Sequence[str], iterations: int = 1000
) -> float:
    """
    Benchmark a matcher implementation.

    Returns:
        Average milliseconds per turn.
    """

    if not texts:
        return 0.0

    start = time.perf_counter()
    for _ in range(iterations):
        for t in texts:
            matcher.find_all(t)
    elapsed = time.perf_counter() - start

    total_turns = len(texts) * iterations
    ms_per_turn = (elapsed / total_turns) * 1000
    return ms_per_turn


def run_benchmark(
    transcripts_path: str | Path,
    cues_path: str | Path,
    k_values: Iterable[int],
    iterations: int = 1000,
) -> None:
    transcripts_path = Path(transcripts_path)
    cues_path = Path(cues_path)

    conversations = parse_transcripts(transcripts_path)
    pairs = agent_turns_after_patient(conversations)
    texts: List[str] = [conv.turns[idx].text for conv, idx in pairs]

    if not texts:
        print("No eligible agent turns found (agent after patient).")
        return

    raw_cues = load_raw_cues(cues_path)
    base_patterns = build_cue_patterns(raw_cues)

    print(f"Loaded {len(conversations)} conversations and {len(texts)} agent turns.")
    print(f"Base cue patterns: {len(base_patterns)}")
    print()
    print(f"{'k':>5} | {'method':>10} | {'ms/turn':>10} | {'speedup_vs_regex':>16}")
    print("-" * 50)

    for k in k_values:
        patterns_k = expand_to_k(base_patterns, k)

        aho = AhoCorasickMatcher(patterns_k)
        regex = RegexBaselineMatcher(patterns_k)

        ms_aho = _benchmark_matcher(aho, texts, iterations=iterations)
        ms_regex = _benchmark_matcher(regex, texts, iterations=iterations)

        speedup = (ms_regex / ms_aho) if ms_aho > 0 else float("inf")

        print(f"{k:5d} | {'aho':>10} | {ms_aho:10.4f} | {'-':>16}")
        print(f"{k:5d} | {'regex':>10} | {ms_regex:10.4f} | {speedup:16.2f}")
        print("-" * 50)


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Benchmark repair-cue matchers (Aho–Corasick vs k-regex)."
    )
    parser.add_argument(
        "--transcripts",
        type=str,
        default="AI engineer assignment/AI engineer assignment transcripts.txt",
        help="Path to transcripts file.",
    )
    parser.add_argument(
        "--cues",
        type=str,
        default="solution/repair_cues.txt",
        help="Path to repair cues file.",
    )
    parser.add_argument(
        "--k",
        type=str,
        default="10,50,200",
        help="Comma-separated list of k values (number of patterns).",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=1000,
        help="Number of iterations over the transcripts for each benchmark.",
    )

    args = parser.parse_args(argv)

    k_values = [int(x.strip()) for x in args.k.split(",") if x.strip()]

    run_benchmark(
        transcripts_path=args.transcripts,
        cues_path=args.cues,
        k_values=k_values,
        iterations=args.iterations,
    )


if __name__ == "__main__":
    main()
