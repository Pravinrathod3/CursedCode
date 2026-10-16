# 07 — Test Harness & Outcome Classification

## Challenge structure

Each challenge should define:
- Stable challenge ID
- Function signature
- Statement and constraints
- Starter code
- Concept tags
- Difficulty
- At least 3 visible tests
- At least 5 hidden tests
- Expected return semantics

Include edge cases, not just happy paths.

## Required outcomes

| Outcome | Meaning |
|---|---|
| `passed` | Execution completed and output matches expected result |
| `wrong_output` | Execution completed but result differs |
| `runtime_error` | Code crashed or was killed by a resource limit |
| `timeout` | Code exceeded the allowed execution time |

Keep infrastructure failures separate from these learner-code outcomes.

## Comparison strategy

Define comparison semantics consistently:
- For the required Python function challenges, compare normalized return values rather than terminal formatting when possible.
- Do not use overly permissive string normalization that makes wrong answers pass.
- Treat missing return values, unexpected types, and malformed results consistently.
- Test the harness itself using known-good and known-bad programs.

## Visible vs hidden

Visible tests may include call/input, expected output, actual output, and outcome.

Hidden tests should return only safe outcome status and permitted aggregate counts. Do not reveal input, expected output, actual output, raw exception, or stack trace.

## Harness failure modes

- Missing test result → never assume passed.
- Invalid runner response → infrastructure/runner error.
- Runner timeout → distinguish learner timeout from upstream service timeout if the runner can report it.
- Output truncation → classify according to runner contract; do not compare truncated output as if complete.
- Partial execution → never report full acceptance.
- Hidden-test exception → retain restricted diagnostics; return only safe summary.

## Acceptance tests

For each of at least three challenges, test four submissions:
1. Correct program
2. Wrong output
3. Runtime exception
4. Infinite loop / timeout

Verify every expected label. Then test that hidden data cannot be extracted through output, exceptions, or hint requests.
