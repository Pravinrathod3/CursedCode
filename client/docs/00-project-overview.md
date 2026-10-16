# 00 — Project Overview

## Product

**Debug Dojo** is a coding coach that helps beginner programmers locate and understand mistakes. It is not an answer-copying chatbot.

## Primary user journey

1. Browse challenges.
2. Choose a challenge by difficulty or concept.
3. Read the problem statement and examples.
4. Write code in the editor.
5. Run or submit the code.
6. Review test outcomes and a plain-language explanation.
7. Request progressive hints when stuck.
8. Try again and review recurring mistakes.
9. Receive a targeted next challenge.

## Main pages

- `/problems` — searchable challenge list
- `/problems/:challengeId` — coding workspace
- `/progress` — learner progress and concept mastery
- Optional `/` — landing page or redirect to `/problems`

## Challenge content minimum

The project brief requires:
- At least 10 challenges
- At least 3 difficulty levels
- At least 4 concepts
- At least 3 visible tests and 5 hidden tests per challenge
- Four judge challenges: `last-k-total`, `countpasses`, `first-n-squares`, and `middlethree`

The UI may display visible test details. Hidden tests must remain hidden; display only safe aggregate outcomes.

## Non-goals for the hackathon

- Supporting multiple learner languages; start with one language (Python).
- Building a complete production-grade online judge from the frontend.
- Giving complete solutions by default.
- Making claims of mastery based on one successful attempt.
- Using official JJK artwork or character assets.

## Definition of a successful demo

A judge can open a challenge, submit code that fails, see the correct result classification, request hints without receiving the full solution, make another attempt, and see the learner profile recommend targeted practice.
