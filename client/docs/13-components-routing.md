# 13 — Components & Routing

## Routes

| Route | Page | Purpose |
|---|---|---|
| `/` | Redirect or landing | Send learner to `/problems` |
| `/problems` | `ProblemsPage` | Browse/search/filter challenges |
| `/problems/:challengeId` | `ProblemWorkspacePage` | Solve one challenge |
| `/progress` | `ProgressPage` | Mastery, recurring mistakes, recommendation |
| `*` | `NotFoundPage` | Friendly unknown-route state |

## Shared layout

- `AppHeader`: brand, navigation, learner menu if applicable
- `AppBreadcrumbs`: uses shadcn/ui Breadcrumb
- `PageContainer`: consistent width and spacing
- `AppSidebar`: optional on desktop; avoid spending too long on it

## Recommended shadcn/ui components

Add components only as needed:
- Button
- Card
- Badge
- Breadcrumb
- Input
- Select
- Tabs
- Resizable
- ScrollArea
- Separator
- Tooltip
- Dialog
- DropdownMenu
- Skeleton
- Progress
- Accordion
- Alert
- Avatar (optional)
- Sonner integration for toasts

## Toaster setup

Mount the Sonner `<Toaster />` once at the application root/provider level. Use `toast.success`, `toast.error`, or neutral toast messages for brief events. Avoid mounting a separate toaster in every page.

## Component naming

Use PascalCase component files. Use feature-oriented names, e.g. `HintLadder`, `HiddenTestSummary`, `RecurringMistakeCard`.

## Acceptance checklist

- [ ] All routes resolve
- [ ] Unknown route has a helpful page
- [ ] Breadcrumbs reflect current challenge
- [ ] Toaster mounted once
- [ ] Shared UI components use design tokens
