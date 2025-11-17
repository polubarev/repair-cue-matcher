# Conversational Agent Repair-Cue Assignment — Implementation Plan

## 1. Clarify Goals and Constraints

1. Detect “repair cues” in agent turns using a multi-pattern matcher whose per-turn complexity is **O(L + M)** (L = length of the turn and M = number of matches), independent of the number of cue patterns `k`.
2. Normalize text (NFC, case-folding, accent-insensitive) so English and Spanish cues are matched robustly.
3. Build a **regex baseline** (k independent regexes) and compare runtimes at `k ∈ {10, 50, 200}` using the provided transcripts.
4. Enforce the **“fire only after patient turn”** constraint when integrating the matcher at conversation level.
5. Produce a cue list file with **≥ 40 cues** and a short KPI write-up (robustness/recovery, comprehension quality, friction).

---

## 2. Data & File Layout

1. Use the provided files:
   - `AI engineer assignment/AI engineer assignment transcripts.txt`: 10 example conversations.
   - `AI engineer assignment/AI engineer assignment repair cues.txt`: starter cue list.
2. Plan final artifacts:
   - `repair_cues.txt`: expanded cue list (≥ 40 cues) grouped by category.
   - `agent_kpi/` Python package for core logic.
   - `agent_kpi/benchmark.py`: micro-benchmark script.
   - `kpi_writeup.md`: short written answers on KPI usage.

---

## 3. Text Normalization Design

Goal: make matching robust across casing and accents while keeping the cue list readable.

1. **Normalization pipeline** for both cues and turns:
   1. Apply Unicode NFC normalization.
   2. Convert to a **case-folded** representation using `str.casefold()` (handles more than `lower()`).
   3. Apply **accent-insensitive** matching:
      - Normalize to NFD (`unicodedata.normalize("NFD", text)`).
      - Strip combining marks (`unicodedata.category(ch) != "Mn"`).
      - Optionally keep punctuation (e.g., `?`, `¿`) but ignore it for word-boundary logic.
2. Provide a single helper function:
   - `normalize(text: str) -> str` that encapsulates this pipeline.
3. Apply the **same normalization** to:
   - All phrases from `repair_cues.txt`.
   - Every agent turn before running either matcher (Aho–Corasick or regex baseline).

---

## 4. Cue List Expansion (≥ 40 Cues)

Goal: expand the starter cue list into a richer taxonomy while keeping categories intuitive.

1. Keep existing categories and expand:
   - `[ASK_TO_REPEAT]`
   - `[REPHRASE]`
   - `[HEARING_ISSUES]`
   - `[CONFIRMATION]`
2. Optionally add:
   - `[APOLOGY]` (e.g., “sorry, I didn’t catch that”).
   - `[CLARIFICATION]` (e.g., “just to be clear…”).
3. For each category, brainstorm **English and Spanish** variants:
   - ASK_TO_REPEAT: “could you repeat that”, “say that one more time”, “¿podría repetir eso?”, “disculpe, no escuché bien”, etc.
   - REPHRASE: “let me say that another way”, “déjeme explicarlo de otra forma”, etc.
   - HEARING_ISSUES: “the line is bad”, “se corta la llamada”, etc.
   - CONFIRMATION: “just to make sure I understood”, “solo para estar seguro”, etc.
4. Store cues in `repair_cues.txt` with the existing INI-style format:
   - Each category in brackets on its own line.
   - One cue per line under that category.
5. During loading, read all cues into a structure:
   - `List[Tuple[normalized_phrase, category, raw_phrase]]`
   - Keep `raw_phrase` for reporting; use `normalized_phrase` in the matcher.

---

## 5. Multi-Pattern Matcher (Aho–Corasick)

Goal: **O(L + M)** per agent turn, independent of `k`.

1. **Data structure:**
   - Implement an Aho–Corasick automaton from scratch:
     - Trie nodes store:
       - `children: dict[char, node_id]`
       - `fail: node_id` (failure link)
       - `outputs: list[pattern_id]` (all patterns ending at this node)
   - Keep a `patterns` array where each `pattern_id` stores:
     - `phrase`, `category`, `raw_phrase`.
2. **Construction (offline, once per pattern set):**
   1. Insert each normalized cue into the trie.
   2. Build failure links with BFS.
   3. Propagate outputs through failure links (so outputs accumulate).
3. **Matching algorithm (per turn):**
   1. Normalize the input turn string.
   2. Iterate over characters:
      - Follow `children`; if missing, follow `fail` links until root or match.
      - Emit all `outputs` at the current node as matches.
   3. Record matches as:
      - `(start_idx, end_idx, category, raw_phrase)` or similar.
4. **Complexity argument:**
   - Construction is `O(total_pattern_length * alphabet)` amortized, done once.
   - Per turn:
     - Each character leads to at most one forward transition plus a bounded number of failure transitions, so total is linear in `L`.
     - Reporting matches is `O(M)`.
   - So runtime is `O(L + M)` and does not depend linearly on `k` at query time.
5. Encapsulate in a class:
   - `AhoCorasickMatcher` with:
     - `__init__(self, patterns: list[CuePattern])`
     - `find_all(self, text: str) -> list[Match]`

---

## 6. Naive k-Regex Baseline

Goal: Provide a clear-performance baseline using independent regexes for each cue.

1. Build one regex per cue:
   - Normalize each cue.
   - Escape special characters or use simple substring regex (`re.escape`).
   - Optionally enforce rough word boundaries using `\b` where appropriate.
2. Compile all regexes into a list:
   - `compiled = [(pattern_id, re.compile(regex_str))]`.
3. For each normalized turn:
   - Run each regex with `.finditer()` and collect matches.
4. Complexity:
   - Roughly `O(k * L)` per turn (plus output cost), which should be slower than Aho–Corasick for large `k`.

---

## 7. Micro-Benchmark Design

Goal: Compare runtimes of Aho–Corasick vs k-regex for `k ∈ {10, 50, 200}`.

1. **Pattern subsets:**
   - Use the full expanded cue list as the base.
   - For `k = 10` and `k = 50`, take stable subsets (e.g., first N cues grouped across categories).
   - For `k = 200`, either:
     - Use all unique cues plus systematically generated variants (adding “please”, minor rephrasings, punctuation variants), or
     - Repeat some cues if needed (acceptable for stressing performance, but will be documented).
2. **Benchmark dataset:**
   - Load all 10 transcripts from `AI engineer assignment transcripts.txt`.
   - Parse into turns; for the benchmark, we can:
     - Focus on **agent turns** (realistic) and optionally include patient turns for volume.
3. **Timing protocol:**
   1. Normalize all turns once and keep them in memory.
   2. For a given `k` and matcher implementation:
      - Build matcher (construction time measured separately if desired).
      - Run a loop over all turns for multiple iterations (e.g., 1k–10k iterations) to get stable timing.
      - Measure wall-clock time with `time.perf_counter()`.
   3. Compute metrics:
      - `ms_per_turn = total_time / (num_turns * iterations) * 1000`.
      - Optionally `tokens_per_second` where tokens = words or characters.
4. **Report format:**
   - Table with rows for each `(k, method)` pair:
     - Columns: `k`, `method`, `ms/turn`, `speedup_vs_regex`.
   - Brief interpretation: e.g., “At k=200, Aho–Corasick is ~X× faster than regex baseline.”

---

## 8. Conversation Integration (“Fire Only After Patient Turn”)

Goal: Ensure repair-cue detection is evaluated only in appropriate conversational context.

1. **Turn parsing:**
   - Parse transcripts into a list of `(speaker, text)` turns by detecting lines beginning with `AGENT:` and `PATIENT:`.
   - Strip speaker labels from `text` before matching.
2. **Integration rule:**
   - Only **run the matcher on agent turns that directly follow a patient turn**.
   - Pseudocode:
     - For `i` from 1 to `len(turns)-1`:
       - If `turns[i-1].speaker == "PATIENT"` and `turns[i].speaker == "AGENT"`:
         - Run matcher on `turns[i].text`.
3. **Output structure:**
   - For each agent turn considered:
     - Store matches and link them to:
       - Conversation ID, turn index, and the preceding patient turn.
4. This rule ensures we measure repair behavior **as a reaction to potential misunderstanding in patient speech**, not in isolation.

---

## 9. KPI Computation and Usage

Goal: Define how to use detected cues to build meaningful KPIs.

1. **Robustness/Recovery KPI:**
   - Metric ideas:
     - `repair_cues_after_misunderstanding / num_misunderstanding_events` (how often the agent attempts repair when needed).
     - `repair_success_rate`: proportion of misunderstandings that are followed by a successful clarification (optional if labels are available).
   - Interpretation:
     - Higher appropriate repair-cue usage after ambiguous/noisy patient turns ⇒ better recovery behavior.
2. **Comprehension Quality KPI:**
   - Metric ideas:
     - `repair_cues_per_100_agent_turns` or `per_minute`.
   - Interpretation:
     - For similar call types, **lower** repair-cue frequency (while still recovering when necessary) suggests better baseline comprehension (ASR/NLU).
3. **Friction KPI:**
   - Metric ideas:
     - Distribution of cue categories over time (e.g., more `[ASK_TO_REPEAT]` + `[HEARING_ISSUES]` early in calls).
     - Sequences like multiple repair cues in a short span as signals of **conversational friction**.
   - Interpretation:
     - Higher clustering of repair cues, especially hearing/ASR-related ones, suggests patient frustration or poor channel quality.
4. Prepare a **½–1 page write-up** (`kpi_writeup.md`) summarizing:
   - Which metrics we propose.
   - How they’d be monitored over time.
   - Potential trade-offs (e.g., under- vs over-use of repair cues).

---

## 10. Code Structure and Testing Plan

1. **Module layout (Python):**
   - `agent_kpi/normalization.py`: `normalize(text)` and helpers.
   - `agent_kpi/patterns.py`: load and normalize cues from `solution/repair_cues.txt`.
   - `agent_kpi/aho_matcher.py`: Aho–Corasick implementation.
   - `agent_kpi/regex_baseline.py`: k-regex matcher.
   - `agent_kpi/integration.py`: transcript parsing and “fire only after patient turn” logic.
   - `agent_kpi/benchmark.py`: micro-benchmark CLI.
2. **Testing:**
   - Unit tests for:
     - Normalization (accent-insensitivity, case-folding).
     - Aho–Corasick vs simple substring search on small examples.
     - Parity between Aho–Corasick and regex baseline on a small synthetic dataset.
     - Conversation parsing and “fire only after patient turn” behavior.
3. **CLI / usage examples:**
   - Simple script taking:
     - `--transcripts path` and `--cues path`.
     - Mode: `match`, `benchmark`, or `kpi`.
   - Output: matches per turn and KPI summary.

---

## 11. Execution Order (Practical Steps)

1. Implement `normalize()` and verify on small English/Spanish examples.
2. Expand `repair_cues.txt` to ≥ 40 cues across categories.
3. Implement and test Aho–Corasick matcher on a few handcrafted turns.
4. Implement regex baseline and verify it returns the same matches as Aho–Corasick on small tests.
5. Implement transcript parsing + “fire only after patient turn” integration.
6. Implement micro-benchmark script and collect runtimes for `k = 10, 50, 200`.
7. Compute and describe KPIs using the detected matches from the transcripts.
8. Finalize the KPI write-up and method note (5–8 lines) summarizing the data structure and complexity.

