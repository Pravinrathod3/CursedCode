# 04 — Problem Listing

## Purpose

Help learners find the next suitable challenge without overwhelming them.

## Layout

- App header with Debug Dojo identity and navigation
- Page title and short description
- Search input
- Filters: difficulty, concept, completion status
- Challenge list/grid
- Optional progress summary
- Empty state when no challenge matches

## Challenge card fields

- Title
- Short description
- Difficulty: Beginner / Intermediate / Advanced
- Concept tags
- Estimated time (only if curated; do not invent)
- Status: New / Attempted / Solved
- CTA: “Enter training”

## Behavior

- Search matches title, description, and concept tags.
- Filters can be combined.
- Clearing filters restores all challenges.
- Keep filters in URL query parameters if simple to implement.
- A solved status must come from the backend or clearly labelled mock data.
- Use pagination or virtualization only if the dataset requires it.

## UI components

- shadcn/ui: Input, Button, Card, Badge, Select, DropdownMenu, Skeleton, Breadcrumb
- lucide-react: Search, SlidersHorizontal, ArrowUpRight, CheckCircle2, Clock3

## States

- Loading: skeleton cards
- Empty: “No challenges match these filters”
- Error: inline alert and retry action
- Success: challenge cards

## Acceptance checklist

- [ ] Search works
- [ ] Difficulty and concept filters work
- [ ] Challenge cards have accessible links/buttons
- [ ] Empty and loading states exist
- [ ] Theme and spacing match the design system
