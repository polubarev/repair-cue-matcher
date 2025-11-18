## KPI Usage of Repair Cues

The KPIs below are defined for an **AI conversational agent** that handles outbound calls and uses repair cues as part of its dialogue policy.

### 1. Robustness / Recovery KPI

- **Idea:** How often does the agent try to fix potential misunderstandings when they happen.
- **Metric:** `repair_cues_after_patient / unclear_patient_turns`, where “unclear” is approximated from signals like low ASR confidence or explicit patient confusion (e.g., “what?”, “¿cómo?”).
- **Example:** In 100 calls we detect **200** unclear patient turns and the agent uses a repair cue after **160** of them → robustness = `160 / 200 = 0.8`. Around **0.7–0.9** is healthy; much lower means the agent often ignores confusion, much higher may sound repetitive.

### 2. Comprehension Quality KPI

- **Idea:** How well the agent understands patients on the first try.
- **Metrics:** Repair-cue rates per 100 agent turns, split into:
  - “Failure-like” cues (`[ASK_TO_REPEAT]`, `[HEARING_ISSUES]`).
  - “Safety/confirmation” cues (`[CONFIRMATION]`).
- **Example:** On 1,000 reminder calls:
  - Model A: **5** repair cues / 100 turns, with **2** failure-like.
  - Model B: **15** repair cues / 100 turns, with **12** failure-like.
  - If outcomes are similar, Model A has better comprehension (fewer true failures); Model B likely has weaker ASR/NLU or a noisier channel.

### 3. Friction / Patient Experience KPI

- **Idea:** How much frustration or friction the agent creates in the conversation.
- **Metrics:** Patterns over time, e.g.:
  - Number of repair cues within a short window (e.g., ≥ 3 in 5 turns).
  - Longest streak of consecutive agent turns with repair cues.
- **Example:** In one call the agent uses repair cues **7** times, with **5** in a row like “you’re breaking up”, “one more time please”. This is a high-friction call and should be flagged for QA. If many calls for the same clinic/carrier show similar streaks, that segment likely has telephony or comprehension issues.
