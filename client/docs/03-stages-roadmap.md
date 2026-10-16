# 03 — Frontend Stages & 24-Hour Roadmap

## Stage 0 — Project foundation (Hour 0–2)

Deliver:
- React + TypeScript + Vite app
- Tailwind and shadcn/ui configured
- Router and app shell
- Theme tokens and responsive layout
- Sonner toaster mounted once near the app root
- Shared types and mock data

Acceptance:
- App starts with one documented command.
- No console errors.
- Theme is consistent across routes.

## Stage 1 — Problem listing (Hour 2–4)

Deliver:
- Search field
- Difficulty filters
- Concept tags
- Challenge cards/table
- Empty and loading states

Acceptance:
- User can search and filter local challenge data.
- Each challenge links to its workspace.

## Stage 2 — Main problem workspace (Hour 4–7)

Deliver:
- Breadcrumbs
- Problem statement panel
- Examples and constraints
- Editor panel
- Run and Submit actions
- Responsive layout

Acceptance:
- Learner can read the problem and edit code.
- Panels remain usable at common laptop widths.

## Stage 3 — Compiler/runner UX (Hour 7–10)

Deliver:
- Submission status
- Pending/loading state
- Compile/runtime details that are safe to show
- Run and submit request handling

Acceptance:
- Duplicate requests are prevented.
- API errors are clearly surfaced.
- No success state is shown before a confirmed response.

## Stage 4 — Test-case engine UI (Hour 10–12)

Deliver:
- Visible test list
- Per-test outcome badges
- Safe hidden-test summary
- Runtime and timeout states

Acceptance:
- All four outcome labels render correctly.
- Hidden test input/expected/actual output never appears.

## Stage 5 — Hints (Hour 12–14)

Deliver:
- Progressive hint panel
- Locked/unlocked hint states
- Request-next-hint action
- Loading and failure states

Acceptance:
- Hints appear in order.
- The UI does not invent hints or bypass backend authorization.

## Stage 6 — Solution policy (Hour 14–15)

Deliver:
- Staged explanation/solution panel
- Optional gated reveal based on product policy
- Clear distinction between hint, explanation, and solution

Acceptance:
- Complete solutions are not presented as ordinary hints.
- Backend response controls what the learner may see.

## Stage 7 — Progress and recommendations (Hour 15–18)

Deliver:
- Concept mastery overview
- Recurring mistake cards
- Recommended next challenge with reason
- Attempt history, if time permits

Acceptance:
- Labels come from server evidence.
- Recommendation reason is visible.

## Stage 8 — Integration, testing, polish (Hour 18–22)

Deliver:
- Real API connection
- Responsive and keyboard testing
- API error handling
- Hostile/malformed response UI testing
- Demo path

## Stage 9 — Freeze and demo (Hour 22–24)

Deliver:
- README
- Stable deployed URL
- Seeded demo account or pseudonymous learner
- Five-minute demo script
- No last-minute visual refactors unless necessary

## Priority rule

If time slips, preserve this order:
1. Working problem → editor → submit → results flow
2. Hidden-test-safe output
3. Hints
4. Recurring mistakes and next challenge
5. Visual polish and optional animations
