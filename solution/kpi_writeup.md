## KPI Usage of Repair Cues

### 1. Robustness / Recovery KPI

- **Definition:** Use the frequency of repair cues that occur immediately after patient turns as a proxy for how actively the agent attempts to recover from misunderstandings or low-ASR moments.
- **Example metric:** For each conversation, track `repair_cues_after_patient / num_patient_turns_with_potential_issues`. In practice, “potential issues” can be approximated by noisy ASR confidence, long pauses, overlapping speech, or explicit patient confusion phrases (“what?”, “¿cómo?”).
- **Interpretation:** A higher rate of appropriate repair cues following problematic patient turns suggests better recovery behavior—i.e., the agent proactively clarifies rather than ignoring uncertainty. However, extremely high counts might indicate that the agent is over-triggering repair, which can itself cause friction.

### 2. Comprehension Quality KPI

- **Definition:** Use overall repair-cue rate as a proxy for the agent’s baseline comprehension performance (ASR + NLU) under typical conditions.
- **Example metrics:**
  - `repair_cues_per_100_agent_turns` for a given call type, language, and channel.
  - `repair_cues_per_minute` segmented by scenario (e.g., outbound reminders vs follow-ups).
- **Interpretation:** For comparable cohorts of calls, a **lower** baseline repair-cue rate generally indicates better comprehension quality: the agent understands patients on first pass more often and does not need to re-ask or rephrase. When comparing models or ASR front-ends, we would expect the better system to show a consistent downward shift in these rates while still maintaining sufficient recovery behavior when needed.

### 3. Friction / Patient Experience KPI

- **Definition:** Use patterns and clustering of repair cues to approximate conversational friction and patient frustration.
- **Example metrics:**
  - Short-window density: number of repair cues within a sliding window of N turns or T seconds (e.g., “≥ 3 cues in 5 turns”).
  - Category mix: relative share of `[HEARING_ISSUES]` vs `[ASK_TO_REPEAT]` vs `[REPHRASE]` vs `[CONFIRMATION]` cues, which captures whether friction is due to channel quality, language mismatch, or clarification style.
  - Streak length: longest streak of consecutive agent turns containing repair cues in a call.
- **Interpretation:** High clustering of repair cues, especially hearing-related ones (“you’re breaking up”, “no se escucha bien”), is a strong signal of technical or conversational friction and often correlates with lower patient satisfaction. A healthy system will show occasional, contextually appropriate repair cues but few long streaks or bursts, and improvements to ASR, telephony, or dialogue policy should reduce these friction indicators over time.

### 4. Operational Use

- Track these KPIs over time and slice by **language**, **clinic**, **call type**, and **model version** to localize regressions.
- Use thresholds (e.g., “> X repair cues per minute” or “≥ Y cues in a 5-turn window”) to flag problematic calls for human QA review.
- Combine repair-cue KPIs with outcome metrics (successful scheduling, call duration, transfer to human) to understand which repair behaviors correlate with good outcomes vs. frustration, then feed those insights back into agent design and policy tuning.

