# 15 — Accessibility, Loading, Empty & Error States

## Accessibility

- Use semantic buttons, links, headings, lists, and form labels.
- Every icon-only button needs an accessible name.
- Maintain visible keyboard focus.
- Ensure dialogs trap focus and return focus on close.
- Do not use color alone for pass/fail status.
- Keep text and controls sufficiently contrasted against dark surfaces.
- Support keyboard navigation for tabs, menus, filters, and hint controls.
- Respect reduced-motion preferences.
- Announce important submission status changes through accessible live regions where appropriate.

## Required states

### Problem listing
- Loading skeleton
- No challenges available
- No search/filter results
- API error with retry

### Editor
- Starter code loading
- Ready to edit
- Editor component unavailable, with textarea fallback if feasible
- Reset confirmation

### Submission
- Queued
- Running
- Completed
- Request failed
- Rate limited, if backend provides this state

### Test results
- Passed
- Wrong output
- Runtime error
- Timeout
- Unknown/malformed response fallback

### Hints
- No hints requested
- Request in progress
- Hint available
- No more hints available
- Hint request failed

### Learner progress
- Loading
- No history yet
- Profile loaded
- Profile unavailable

## Error message guidelines

Good:
- “The submission service could not be reached. Try again.”
- “Your code exceeded the time limit.”
- “This test produced a different result than expected.”
- “We couldn't load your progress.”

Avoid:
- Raw server stack traces
- Hidden-test input or expected output
- Secrets, environment values, internal filesystem paths
- Vague “Something broke” messages without a recovery action

## Final QA checklist

- [ ] Can navigate the app using keyboard only
- [ ] Buttons announce their purpose
- [ ] All async actions show pending state
- [ ] Empty and error states are designed
- [ ] API outage is not labelled as learner runtime error
- [ ] No hidden-test information appears in the DOM or browser console
- [ ] Mobile layout has no horizontal overflow
- [ ] Reduced motion is respected
