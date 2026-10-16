# 14 — Frontend API Contracts

The backend owns execution, test results, hidden-test secrecy, hint policy, and learner modeling. Agree exact JSON shapes with the backend team before integration. The shapes below are proposed frontend contracts, not claims about an already implemented API.

## Submit code

`POST /api/submit`

Request:

```json
{
  "learner_id": "pseudonymous-learner-id",
  "challenge_id": "last-k-total",
  "code": "def last_k_total(marks, k):\n    return sum(marks[-k:])"
}
```

Proposed response shape:

```json
{
  "submission_id": "sub_123",
  "learner_id": "pseudonymous-learner-id",
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
  "explanation": "The visible examples pass. Review the input boundary cases."
}
```

Important: the hidden test entries above intentionally contain only an ID and outcome. Do not add hidden input, expected output, actual output, or raw exception text.

## Request next hint

`POST /api/hint`

Request:

```json
{
  "submission_id": "sub_123"
}
```

Proposed response:

```json
{
  "submission_id": "sub_123",
  "hint_index": 1,
  "hint": "Check how your code behaves when the input is empty."
}
```

## Get learner profile

`GET /api/learner/{learner_id}`

Proposed response:

```json
{
  "learner_id": "pseudonymous-learner-id",
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
    "reason": "Practise loop boundaries, which appeared in two recent challenges."
  }
}
```

## Frontend API rules

- Put endpoint calls in feature service modules.
- Use a shared API client with a configurable base URL.
- Validate response fields before rendering.
- Handle network errors separately from code execution outcomes.
- Never trust the frontend to enforce authorization or hint safety.
- Do not put secrets in Vite variables prefixed with `VITE_`.
- Use mock data only in clearly marked development mode.
- Confirm with backend developers whether `Run` and `Submit` call the same endpoint or separate endpoints.
