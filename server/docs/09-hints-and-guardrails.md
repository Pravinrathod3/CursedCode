# 09 — Progressive Hints & Guardrails

## Requirement

Offer at least three hints per failure, each more specific than the previous hint. None may reveal the complete solution, even if a learner asks for the answer or combines all hints.

## Hint ladder

1. **Conceptual nudge** — identify a relevant concept or class of edge cases.
2. **Inspection direction** — suggest which branch, loop, condition, or assumption to inspect.
3. **Specific guidance** — narrow down the likely cause without providing the complete corrected code.

Optional fourth hint: suggest a general technique or manual trace.

## Server-side sequence

1. Verify the submission exists and belongs to the requested pseudonymous learner/context.
2. Determine the next permitted hint index on the server.
3. Build context from safe failure evidence and previous hints.
4. Generate one hint.
5. Validate that it does not include a complete solution or hidden data.
6. Store the hint and return it.
7. Do not let client-supplied indices skip the sequence.

## Leakage prevention

- Do not send hidden test data to the LLM.
- Do not include raw hidden exceptions in the prompt.
- Do not return complete function implementations in hints.
- Keep the hint endpoint separate from submission judging.
- Test the combined hint ladder against hidden tests.
- If a hint fails validation, retry once with stricter constraints or return a deterministic fallback.

## Output validation

Validation can include:
- Maximum length
- No fenced code block containing a complete function
- No known hidden values or private diagnostic content
- No solution-shaped response when a conceptual hint is required
- Optional code-AST checks for obvious full-function leakage, while recognizing that AST checks alone cannot prove a hint is safe

No single heuristic proves a hint cannot leak a solution. The judging test pack must evaluate combined hints against the hidden tests.

## Example

For a loop that starts at a negative index:
1. “Think about what happens when the requested count is larger than the input.”
2. “Trace the first index your loop uses for a short input.”
3. “Check whether your starting index can become negative and how Python treats negative list indices.”

The student must still write the correction.
