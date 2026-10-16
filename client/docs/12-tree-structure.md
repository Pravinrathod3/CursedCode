# 12 — Suggested Frontend Tree Structure

```text
debug-dojo/
├── public/
│   ├── favicon.svg
│   └── og-image.png
├── src/
│   ├── app/
│   │   ├── App.tsx
│   │   ├── router.tsx
│   │   └── providers.tsx
│   ├── components/
│   │   ├── layout/
│   │   │   ├── AppHeader.tsx
│   │   │   ├── AppSidebar.tsx
│   │   │   ├── PageContainer.tsx
│   │   │   └── AppBreadcrumbs.tsx
│   │   ├── problems/
│   │   │   ├── ProblemCard.tsx
│   │   │   ├── ProblemFilters.tsx
│   │   │   ├── ProblemSearch.tsx
│   │   │   └── ProblemList.tsx
│   │   ├── workspace/
│   │   │   ├── ProblemStatement.tsx
│   │   │   ├── CodeEditor.tsx
│   │   │   ├── EditorToolbar.tsx
│   │   │   ├── RunSubmitBar.tsx
│   │   │   ├── SubmissionStatus.tsx
│   │   │   ├── TestResultsPanel.tsx
│   │   │   ├── VisibleTestRow.tsx
│   │   │   ├── HiddenTestSummary.tsx
│   │   │   ├── ExplanationPanel.tsx
│   │   │   ├── HintLadder.tsx
│   │   │   └── SubmissionHistory.tsx
│   │   ├── progress/
│   │   │   ├── MasteryCard.tsx
│   │   │   ├── RecurringMistakeCard.tsx
│   │   │   └── NextChallengeCard.tsx
│   │   └── ui/
│   │       └── # shadcn/ui generated components
│   ├── pages/
│   │   ├── ProblemsPage.tsx
│   │   ├── ProblemWorkspacePage.tsx
│   │   ├── ProgressPage.tsx
│   │   └── NotFoundPage.tsx
│   ├── features/
│   │   ├── problems/
│   │   │   ├── problems.api.ts
│   │   │   ├── problems.types.ts
│   │   │   └── problems.mock.ts
│   │   ├── submissions/
│   │   │   ├── submissions.api.ts
│   │   │   └── submissions.types.ts
│   │   ├── hints/
│   │   │   ├── hints.api.ts
│   │   │   └── hints.types.ts
│   │   └── learner/
│   │       ├── learner.api.ts
│   │       └── learner.types.ts
│   ├── hooks/
│   │   ├── useProblems.ts
│   │   ├── useSubmission.ts
│   │   └── useLearnerProfile.ts
│   ├── lib/
│   │   ├── api-client.ts
│   │   ├── outcome-labels.ts
│   │   ├── utils.ts
│   │   └── validation.ts
│   ├── styles/
│   │   └── globals.css
│   ├── types/
│   │   └── common.ts
│   └── main.tsx
├── docs/
├── .env.example
├── .gitignore
├── components.json
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

## Structure rules

- `pages/` composes screens; it should not contain every detail.
- `components/` holds reusable visual pieces.
- `features/` owns API calls and domain types for each feature.
- `lib/` contains shared utilities and API client setup.
- `components/ui/` is for shadcn/ui-generated primitives.
- Keep mock data separate from production API calls.
- Do not commit `.env` files or API keys.
- Avoid premature abstractions during the 24-hour build; split components when doing so improves clarity or testability.
