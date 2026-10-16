# 13 — Suggested Backend Project Tree

```text
debug-dojo-backend/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── exceptions.py
│   ├── api/
│   │   ├── router.py
│   │   └── routes/
│   │       ├── health.py
│   │       ├── challenges.py
│   │       ├── submissions.py
│   │       ├── hints.py
│   │       └── learners.py
│   ├── schemas/
│   │   ├── challenge.py
│   │   ├── submission.py
│   │   ├── hint.py
│   │   └── learner.py
│   ├── services/
│   │   ├── challenge_service.py
│   │   ├── submission_service.py
│   │   ├── execution_service.py
│   │   ├── outcome_classifier.py
│   │   ├── explanation_service.py
│   │   ├── hint_service.py
│   │   ├── mistake_detector.py
│   │   └── learner_model.py
│   ├── agents/
│   │   ├── state.py
│   │   ├── graph.py
│   │   ├── prompts.py
│   │   ├── output_validation.py
│   │   └── providers.py
│   ├── repositories/
│   │   ├── challenges_repo.py
│   │   ├── submissions_repo.py
│   │   ├── hints_repo.py
│   │   └── learners_repo.py
│   ├── integrations/
│   │   ├── runner_client.py
│   │   ├── supabase_client.py
│   │   └── llm_client.py
│   └── utils/
│       ├── ids.py
│       └── serialization.py
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── security/
│   └── fixtures/
├── scripts/
│   └── seed_challenges.py
├── docs/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Structure rules

- Routes validate and delegate; they should not contain runner or prompt logic.
- Services contain business rules.
- Repositories contain persistence operations.
- `execution_service.py` talks to the restricted runner adapter.
- `outcome_classifier.py` normalizes runner results.
- `agents/` contains bounded LLM workflow code only.
- `learner_model.py` stays deterministic and testable.
- Keep mock integrations explicit and separate from live integrations.
- Avoid creating unnecessary abstractions under hackathon time pressure, but keep the runner boundary clear.
