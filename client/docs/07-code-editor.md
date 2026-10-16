# 07 — Code Editor

## Purpose

Give learners a comfortable place to write and revise code.

## Recommended implementation

Use `@monaco-editor/react` if installation and bundle size are acceptable. Otherwise start with a styled `<textarea>` and replace it later. Do not let editor setup block the submission flow.

## Editor requirements

- Python syntax highlighting when Monaco is used
- Line numbers
- Monospace font
- Starter code loaded from challenge metadata
- User edits preserved between runs
- Reset-to-starter action with confirmation if code has changed
- Copy code action
- Readable focus and selection states
- Optional font-size or theme control only if time permits

## Editor toolbar

- Language badge: Python
- Reset
- Copy
- Optional “Domain Focus” distraction-reduced mode

## Safety

- The editor is not the execution environment.
- Never execute learner code in the browser unless the product explicitly uses a safe browser runtime and the limitations are understood.
- Do not evaluate submitted source with `eval`.
- Treat code as text; never inject it into the DOM as HTML.

## States

- Loading starter code
- Editable
- Submitting (editor may remain editable, but capture a submission snapshot)
- Read-only only when necessary; explain why
- Editor failed to load: show a usable textarea fallback if feasible

## Acceptance checklist

- [ ] Starter code appears
- [ ] Edits persist while navigating within the workspace
- [ ] Run/Submit uses the current code snapshot
- [ ] Reset asks for confirmation if code changed
- [ ] Editor failure does not make the whole page unusable
