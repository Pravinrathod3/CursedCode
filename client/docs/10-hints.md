# 10 — Progressive Hints

## Purpose

Help the learner discover the bug without giving away the full solution.

## Hint ladder

Each failure should offer at least three hints, progressively more specific:
1. Conceptual nudge
2. Direction to inspect
3. Specific debugging guidance

A fourth hint may suggest a general technique, but must still avoid providing the complete solution.

## Interaction

- Display hints in order.
- “Get next hint” requests the next available hint from the API.
- Show locked/unavailable states clearly.
- Keep previous hints visible so the learner can compare them.
- Do not create fake hints on the client.
- If the hint API fails, show retry without losing existing hints.

## UI copy examples

- “Hint 1 — Think about the input boundaries.”
- “Hint 2 — Trace the first and last index used by your loop.”
- “Hint 3 — Check whether your starting index can fall outside the intended range.”

These are illustrative; actual hints should be specific to the challenge and failure.

## Guardrails

- The UI cannot guarantee hint safety by itself.
- The backend should prevent hidden inputs/expected outputs from reaching the LLM.
- The backend must validate or reject hints that contain complete solutions.
- Test the combined hint ladder: merging all hints must not trivially produce a solution that passes every hidden test.
- If a learner asks directly for the answer, the policy remains unchanged.
- Render AI text safely; do not render arbitrary HTML.

## Acceptance checklist

- [ ] Hints unlock progressively
- [ ] Current hint request has a loading state
- [ ] API errors are recoverable
- [ ] No complete code solution appears in hint content
- [ ] Hint history remains visible
