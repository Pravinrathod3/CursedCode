# 00 — Backend Overview

## Purpose

The backend receives code submissions, runs them through a restricted execution service, classifies test outcomes, produces grounded explanations and progressive hints, and updates learner progress.

## Backend responsibilities

- Validate incoming requests.
- Load challenge metadata and test definitions.
- Submit learner code to a restricted runner.
- Classify outcomes using trusted runner results.
- Return safe visible-test details and hidden-test summaries only.
- Generate explanations/hints from sanitized evidence.
- Store attempts, mistake tags, hints, and learner progress in Supabase.
- Recommend a challenge based on recurring mistakes and concept mastery.

## Not backend responsibilities

- Trusting an LLM to decide if code passed.
- Running arbitrary learner code in the FastAPI process.
- Returning hidden test inputs/expected/actual outputs to the client.
- Treating an LLM-generated mastery score as ground truth.
- Storing provider secrets in the database as ordinary learner data.

## Required judge challenges

The challenge set must include:
- `last-k-total`
- `countpasses`
- `first-n-squares`
- `middlethree`

Minimum challenge coverage:
- 10 challenges
- 3 difficulty levels
- 4 concepts
- At least 3 visible tests and 5 hidden tests per challenge

## Main use case

1. Learner submits code.
2. API validates learner/challenge identifiers and code size.
3. Runner executes against configured tests under restrictions.
4. Backend normalizes the runner output into allowed outcomes.
5. Backend creates a sanitized explanation context.
6. Hint workflow generates a non-solution hint when requested.
7. Backend persists submission and updates learner evidence.
8. Learner endpoint returns recurring mistakes, mastery, and a reasoned next challenge.
