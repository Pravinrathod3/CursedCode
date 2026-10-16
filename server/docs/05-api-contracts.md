# 05 — Required API Contracts

The following contracts are proposed to match the project brief and frontend docs. Confirm field names with the team and keep them stable. Use underscore outcome values internally.

## `POST /api/submit`

Request:

```json
{
  "learner_id": "learner_demo_01",
  "challenge_id": "last-k-total",
  "code": "def last_k_total(marks, k):\n    return sum(marks[-k:])"
}
```

Response example:

```json
{
  "submission_id": "sub_0142",
  "learner_id": "learner_demo_01",
  "challenge_id": "last-k-total",
  "visible": [
    {
      "test": 1,
      "call": "last_k_total([10, 20, 30, 40], 2)",
      "expected": "70",
      "got": "70",
      "outcome": "passed"
    }
  ],
  "hidden": [
    { "test": 1, "outcome": "passed" },
    { "test": 2, "outcome": "wrong_output" }
  ],
  "mistake_tags": [],
  "explanation": "Review boundary cases when the requested count exceeds the input length."
}
```

**Hidden results must never contain** input, expected output, actual output, raw exception text, filesystem paths, or runner internals.

Allowed internal outcomes:
- `passed`
- `wrong_output`
- `runtime_error`
- `timeout`

The frontend may map these to display labels “Passed”, “Wrong output”, “Runtime error”, and “Timeout”.

## `POST /api/hint`

Request:

```json
{
  "submission_id": "sub_0142"
}
```

Response:

```json
{
  "submission_id": "sub_0142",
  "hint_index": 1,
  "hint": "Consider how the loop behaves when the input is shorter than the requested count."
}
```

The server controls hint progression. Do not accept an arbitrary hint index from the client as proof that the user may access that hint.

## `GET /api/learner/{learner_id}`

Response:

```json
{
  "learner_id": "learner_demo_01",
  "recurring_mistakes": [
    {
      "category": "off_by_one",
      "challenge_count": 2
    }
  ],
  "mastery": [
    {
      "concept": "loops",
      "estimate": 0.65
    }
  ],
  "next_challenge": {
    "challenge_id": "boundary-practice-01",
    "reason": "Practise loop boundaries, which appeared in two different challenges."
  }
}
```

## Recommended extra endpoints

- `GET /health` — service liveness
- `GET /api/challenges` — list challenge metadata only
- `GET /api/challenges/{challenge_id}` — public challenge statement and visible examples
- `GET /api/submissions/{submission_id}` — optional submission status/history

Do not expose hidden test definitions through challenge endpoints.

## Contract rules

- Validate code size and identifier formats.
- Return consistent errors.
- Distinguish execution failure from infrastructure failure.
- Return only safe, necessary fields.
- Keep examples fictional and free of secrets.
