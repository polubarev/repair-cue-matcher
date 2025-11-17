# Conversational Agent Repair-Cue Assignment — Solution

This repository contains the original assignment materials and an implementation for detecting conversational **repair cues** (e.g., “can you repeat?”, “just to confirm…”) in agent turns, benchmarking an efficient multi-pattern matcher against a naive regex baseline, and outlining KPI usage.

## Layout

- `AI engineer assignment/`
  - `AI engineer assignment.pdf` — original assignment PDF.
  - `AI engineer assignment.md` — Markdown copy of the assignment (for easier reading).
  - `AI engineer assignment transcripts.txt` — 10 example conversations.
  - `AI engineer assignment repair cues.txt` — original starter cue list from the assignment.
- `agent_kpi/` — Python package with the implementation:
  - `normalization.py` — text normalization (NFC, case-fold, accent-insensitive).
  - `patterns.py` — cue loading and k-expansion utilities.
  - `aho_matcher.py` — Aho–Corasick multi-pattern matcher (`O(L + M)` per turn).
  - `regex_baseline.py` — naive k-regex baseline matcher.
  - `integration.py` — transcript parsing and “fire only after patient turn” rule.
  - `benchmark.py` — micro-benchmark CLI (Aho–Corasick vs regex).
- `solution/`
  - `solution_plan.md` — step-by-step implementation plan.
  - `repair_cues.txt` — expanded cue list (≥ 40 cues, EN + ES, categorized).
  - `method_note.md` — data structure, time/memory bounds, O(L + M) justification.
  - `kpi_writeup.md` — short write-up on KPI usage (robustness, comprehension, friction).

## Requirements

- Python **3.9+**.
- No third-party dependencies (standard library only).

Run all commands from the repo root:

```bash
cd "/Users/igor/Personal/DR_asses"
```

## Running the Micro-Benchmark

Compare Aho–Corasick vs naive regex across different numbers of cue patterns:

```bash
# Quick run (faster, less stable numbers)
python -m agent_kpi.benchmark --iterations 50

# Full benchmark (more stable)
python -m agent_kpi.benchmark \
  --transcripts "AI engineer assignment/AI engineer assignment transcripts.txt" \
  --cues "solution/repair_cues.txt" \
  --k 10,50,200 \
  --iterations 100 \                          
  --out-md "solution/last_benchmark_run.md"              
```

This prints a table with, for each `k`:

- `method` — `aho` or `regex`,
- `ms/turn` — average milliseconds per agent turn,
- `speedup_vs_regex` — relative speedup of Aho–Corasick vs regex.

Show all benchmark options:

```bash
python -m agent_kpi.benchmark --help
```

## Inspecting Detected Repair Cues

To see which repair cues are detected in the sample transcripts (using the “fire only after patient turn” rule):

```bash
python scripts/inspect_repair_cues.py
```

## Documentation & KPIs

- Method note (for submission): `solution/method_note.md`
- KPI usage description (robustness, comprehension quality, friction): `solution/kpi_writeup.md`

You can use these markdown files directly as part of the written deliverables for the assignment.
