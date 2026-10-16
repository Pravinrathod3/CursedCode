# 11 — Learner Model & Mastery

## Purpose

Track learning evidence and recommend targeted practice. This should be deterministic and explainable, not a black-box AI score.

## Inputs

- Challenge concept tags
- Submission outcomes
- Hint count/level used before passing
- Mistake categories and challenge IDs
- Recent attempt history

## Mastery estimate

For a hackathon MVP, use a simple documented heuristic or weighted rolling score. Example evidence weights (tune and document):
- Correct without hints: strong positive evidence
- Correct after one or more hints: positive but lower evidence
- Wrong output/runtime error: negative evidence for the relevant concept only when the category is supported
- No attempt: no evidence

Do not claim a particular score is scientifically validated. Store either raw evidence or enough attempt history to recompute it.

## Recurring mistakes

A category is recurring if it appears in at least two different challenges. The API should return the category and the number of distinct challenges that support it.

## Next challenge selection

Simple recommendation algorithm:
1. Find recurring mistakes and weak concepts.
2. Find unsolved challenges tagged with those concepts.
3. Prefer a suitable difficulty level.
4. Avoid repeating the same challenge immediately.
5. Return the selected challenge ID and a reason grounded in the learner's evidence.

Example reason:
“Practise loop boundaries because an off-by-one mistake appeared in two different challenges.”

## Do not do this

- Do not let the LLM invent mastery scores.
- Do not infer skill from one pass alone.
- Do not count repeat failures on the same challenge as cross-challenge recurrence.
- Do not recommend a challenge without an explanation.
- Do not treat hints as evidence of failure; use hint count to contextualize the success.

## API output

`GET /api/learner/{learner_id}` returns:
- recurring mistakes
- mastery per concept
- next challenge
- reason for the recommendation
