# 10 — Mistake Taxonomy & Detection

## Required categories

Keep these five distinct:

| Category | Description | Detection evidence |
|---|---|---|
| `off_by_one` | Loop/index boundary is shifted | Challenge-specific boundary tests and code/error patterns |
| `unhandled_short_input` | Empty or too-short input is not handled | Failure on empty/small input cases |
| `print_not_return` | Function prints instead of returning | Expected return is absent or returned value is `None` while output was printed |
| `boundary_comparison` | Incorrect comparison at a threshold, e.g. `<` vs `<=` | Tests at threshold values plus challenge-specific analysis |
| `mutates_input` | Function unexpectedly changes input | Compare original input snapshot with post-run state, where harness supports it |

## Detection policy

- Use deterministic rules and challenge-specific evidence first.
- LLM may suggest a category, but do not treat an unsupported guess as fact.
- Store confidence/evidence if useful.
- If evidence is ambiguous, leave the failure unclassified rather than inventing a tag.
- Keep `off_by_one` and `boundary_comparison` distinct in the stored taxonomy.

## Recurrence definition

A category is recurring only when it appears in at least **two different challenge IDs** for that learner. Multiple attempts on one challenge do not satisfy this rule.

## Storage fields

Suggested mistake event:
- `learner_id`
- `submission_id`
- `challenge_id`
- `category`
- `evidence_summary`
- `confidence` (optional)
- `created_at`

Do not store hidden test input or expected output in the evidence summary.

## Recommendation use

When a category becomes recurring:
- surface it in the learner profile;
- find an unsolved challenge tagged with the relevant concept/category;
- return a human-readable reason;
- avoid recommending a challenge the learner has already mastered repeatedly, unless spaced review is intentional.
