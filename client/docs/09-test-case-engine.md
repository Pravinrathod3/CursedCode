# 09 — Test Case Engine UI

## Purpose

Present enough evidence for debugging while keeping hidden tests confidential.

## Per-test outcomes

Use these four outcomes exactly in the underlying model:
- `passed`
- `wrong output`
- `runtime error`
- `timeout`

Friendly labels may include spaces and capitalization, but the underlying enum should remain stable.

## Visible tests

For visible tests, display:
- Test number or stable ID
- Input/call
- Expected output
- Actual output, if safely returned
- Outcome
- Safe runtime-limit information, if relevant

## Hidden tests

For hidden tests, display only:
- Test number or opaque label, if allowed
- Outcome
- Aggregate count of passed/failed hidden tests

Never display:
- Hidden input
- Expected output
- Program output for hidden cases
- Raw hidden exception message
- Hidden-test file paths or internal identifiers that expose test data

Do not put hidden details in browser logs, client error reports, toasts, analytics, or LLM prompts.

## Visual design

- Passed: icon + “Passed”
- Wrong output: icon + “Wrong output”
- Runtime error: icon + “Runtime error”
- Timeout: icon + “Timeout”

Use text and icons in addition to color. A filter by outcome is optional.

## Result summary

Example:
- Visible tests: 3/3 passed
- Hidden tests: 4/6 passed
- Overall status: Needs work

The counts must come from the API response; never calculate hidden test contents in the client.

## Acceptance checklist

- [ ] All four outcomes render correctly
- [ ] Visible test data is displayed accurately
- [ ] Hidden tests show safe summaries only
- [ ] Malformed API responses do not crash the page
- [ ] Outcome meaning is understandable without color
