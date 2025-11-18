## KPI Usage of Repair Cues

### 1. Robustness / Recovery KPI

- **Definition:** Use the frequency of repair cues that occur immediately after patient turns as a proxy for how actively the agent attempts to recover from misunderstandings or low-ASR moments.
- **Example metric:** For each conversation, track `repair_cues_after_patient / num_patient_turns_with_potential_issues`. In practice, “potential issues” are hard to observe directly, so we approximate them with low ASR confidence (e.g., `< 0.6`), unusually long silences after ASR output (e.g., `> 4s`), overlapping speech, or explicit patient confusion phrases (“what?”, “¿cómo?”).
- **Interpretation:** A higher rate of appropriate repair cues following problematic patient turns suggests better recovery behavior—i.e., the agent proactively clarifies rather than ignoring uncertainty. However, extremely high counts might indicate that the agent is over-triggering repair, which can itself cause friction.
- **Worked example:** In 100 calls we detect **200** “potentially unclear” patient turns. The agent uses a repair cue after **160** of them:
  - Robustness score = `160 / 200 = 0.8`.
  - **Interpretation:** 0.8 means in 80% of unclear situations the agent actively repairs, which is usually healthy.
  - If this score were **≈ 0.3**, it would indicate that the agent is missing most opportunities to clarify. If it were **> 0.95**, it might mean the agent is overusing repair cues and could feel repetitive or robotic.

### 2. Comprehension Quality KPI

- **Definition:** Use overall repair-cue rate as a proxy for the agent’s baseline comprehension performance (ASR + NLU) under typical conditions, while distinguishing **safety confirmations** from genuine comprehension failures.
- **Example metrics:**
  - `repair_cues_per_100_agent_turns` for a given call type, language, and channel.
  - Separate rates for “failure-like” cues (`[ASK_TO_REPEAT]`, `[HEARING_ISSUES]`) and “safety/confirmation” cues (`[CONFIRMATION]`).
  - `repair_cues_per_minute` segmented by scenario (e.g., outbound reminders vs follow-ups).
- **Interpretation:** For comparable cohorts of calls, a **lower** baseline rate of failure-like cues generally indicates better comprehension quality: the agent understands patients on first pass more often and does not need to re-ask or rephrase. High confirmation usage alone may simply reflect a conservative policy. When comparing models or ASR front-ends, we would expect the better system to show a consistent downward shift in failure-like cue rates while still maintaining enough confirmations to avoid unsafe assumptions.
- **Worked example:** On 1,000 reminder calls we see:
  - Model A: **5 repair cues / 100 agent turns**.
  - Model B: **15 repair cues / 100 agent turns**.
  - Suppose for Model B, **12/15** are `[ASK_TO_REPEAT]` or `[HEARING_ISSUES]`, while for Model A only **2/5** are in those categories and the rest are `[CONFIRMATION]`. If scheduling rates and average call durations are similar, we interpret Model A as having **better comprehension** (fewer true failures). A move from 15 → 5 failure-like cues per 100 over a deployment cycle is a clear improvement; a jump from 5 → 15 would be a regression worth investigating (ASR config change, new prompt, etc.).

### 3. Friction / Patient Experience KPI

- **Definition:** Use patterns and clustering of repair cues to approximate conversational friction and patient frustration.
- **Example metrics:**
  - Short-window density: number of repair cues within a sliding window of N turns or T seconds (e.g., “≥ 3 cues in 5 turns”).
  - Category mix: relative share of `[HEARING_ISSUES]` vs `[ASK_TO_REPEAT]` vs `[REPHRASE]` vs `[CONFIRMATION]` cues, which captures whether friction is due to channel quality, language mismatch, or clarification style.
  - Streak length: longest streak of consecutive agent turns containing repair cues in a call.
- **Interpretation:** High clustering of repair cues, especially hearing-related ones (“you’re breaking up”, “no se escucha bien”), is a strong signal of technical or conversational friction and often correlates with lower patient satisfaction. A healthy system will show occasional, contextually appropriate repair cues but few long streaks or bursts. High-friction segments should be cross-checked against downstream signals like call abandonment rate or negative sentiment detection to confirm that they are truly impacting patient experience, and improvements to ASR, telephony, or dialogue policy should reduce these friction indicators over time.
- **Worked example:** In one 4-minute call, the agent uses repair cues **7 times**, with **5** of them in a cluster of **5 consecutive agent turns**:
  - Short-window density: `5 cues / 5 turns` → very high.
  - Streak length: 5.
  - Category mix: 4 are `[HEARING_ISSUES]` (“you’re breaking up”, “the line is bad”), 1 is `[ASK_TO_REPEAT]`.
  - **Interpretation:** This call is clearly high-friction: the patient is likely frustrated, and telephony quality is suspect. If many calls for the same clinic/carrier show similar numbers (e.g., ≥ 3 cues in any 5-turn window), that segment should be flagged for QA review and possible telephony or routing fixes.

### 4. Operational Use

- Track these KPIs over time and slice by **language**, **clinic**, **call type**, and **model version** to localize regressions.
- Use thresholds (e.g., “> X repair cues per minute” or “≥ Y cues in a 5-turn window”) to flag problematic calls for human QA review.
- Combine repair-cue KPIs with outcome metrics (successful scheduling, call duration, transfer to human) to understand which repair behaviors correlate with good outcomes vs. frustration, then feed those insights back into agent design and policy tuning.
