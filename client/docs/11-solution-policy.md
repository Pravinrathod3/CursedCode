# 11 — Explanation & Solution Policy

## Keep these three things distinct

### Explanation
Describes what the observed failure means and where to investigate. It should be grounded in trusted runner evidence.

### Hint
A progressive nudge that helps the learner discover the correction.

### Complete solution
A full corrected implementation. This should not be returned as a normal hint or shown automatically after failure.

## Suggested policy

For the hackathon, prioritize explanation + hints. If a solution panel is included:
- Keep it separate from the hint ladder.
- Make its availability explicit and controlled by the backend/product policy.
- Do not include complete solutions in ordinary hint responses.
- Do not reveal hidden tests or hidden expected outputs with the solution.
- If the brief's no-answer-away requirement is interpreted strictly, omit complete solution reveal and use a “Review approach” panel instead.

## Frontend behavior

- Use tabs or an accordion for “Explanation”, “Hints”, and optional “Solution policy”.
- Show the explanation immediately after a failed run if the API returns one.
- Request hints through the hint endpoint.
- Do not generate a solution locally as a fallback.
- Do not treat “show solution” as a security feature; it is a product policy control.

## Review approach panel

A safe alternative to full solution reveal:
- Restate the relevant concept
- Ask the learner to inspect a specific branch or boundary
- Offer pseudocode-level direction without a complete implementation
- Link to another practice challenge

## Acceptance checklist

- [ ] Explanation, hint, and solution are visually distinct
- [ ] No solution appears automatically
- [ ] Hint endpoint cannot be bypassed in the UI
- [ ] Backend policy controls solution availability
