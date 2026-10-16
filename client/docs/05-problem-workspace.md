# 05 — Main Problem Workspace

## Purpose

Provide one focused place to understand the challenge, write code, run tests, and receive feedback.

## Desktop layout

- Top: header and breadcrumbs
- Left panel: problem statement, examples, constraints, concepts
- Right panel: editor
- Bottom or right-side tabs: Test Results, Hints, Submission History
- Primary actions: Run Code and Submit Solution

Use a resizable split layout if it can be implemented reliably. If not, use a fixed two-column grid with a responsive stacked layout on smaller screens.

## Responsive behavior

- Desktop: statement and editor side by side
- Tablet: narrower split or tabs for statement/editor
- Mobile: stacked sections; keep Run and Submit easy to reach
- Avoid making multiple nested scroll areas impossible to navigate

## Workspace state

Suggested state fields:
- `challenge`
- `sourceCode`
- `activeTab`
- `runStatus`
- `submissionId`
- `testResults`
- `visibleExplanation`
- `availableHints`
- `errorMessage`

Avoid a single giant component. Split the workspace into statement, editor, actions, results, hints, and history components.

## UX rules

- Warn before navigating away if there are unsaved edits, if feasible.
- Preserve editor content while switching tabs.
- Keep the selected challenge in the breadcrumb.
- Run and Submit should have different intent and labels.
- Disable buttons during active requests.
- Do not claim “accepted” unless the server confirms all required tests passed.

## Acceptance checklist

- [ ] Breadcrumbs work
- [ ] Problem and editor are visible on desktop
- [ ] Layout stacks on mobile
- [ ] Editor state survives tab changes
- [ ] Loading, error, and success states are handled
