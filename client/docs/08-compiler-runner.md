# 08 — Compiler / Runner UI

## Terminology

The first supported language is Python, so the interface can say “Run code” or “Execute submission” rather than implying a separate compile step. If the backend has a compile phase for other languages later, expose it as a distinct status.

## Actions

- **Run code:** fast feedback against the permitted test set, according to backend contract.
- **Submit solution:** full judge evaluation, including hidden tests.

The exact difference must be agreed with the backend team and documented. Do not imply that Run checks only visible tests unless that is actually implemented.

## Status model

Suggested request states:
- `idle`
- `queued`
- `running`
- `completed`
- `failed`

Suggested final outcomes:
- `passed`
- `wrong_output`
- `runtime_error`
- `timeout`

Map API values to friendly labels in one shared helper.

## UI behavior

- Show spinner and status text while queued/running.
- Disable duplicate submissions.
- Show elapsed time only if measured by the backend.
- If request fails due to network/server error, show an infrastructure error—not a learner runtime error.
- Preserve the editor content after failure.
- Provide a retry action for transient infrastructure failures.

## Security and error detail

- Display only approved diagnostics.
- Never show raw hidden-test exceptions or private runner paths.
- Do not expose environment variables, runner internals, or server logs.
- A resource-limit kill should be reported as a runtime error with the relevant limit if the API provides it safely.

## Acceptance checklist

- [ ] Run and Submit have clear meanings
- [ ] Loading state appears immediately
- [ ] Duplicate requests are prevented
- [ ] Timeout differs from wrong output
- [ ] Network failure differs from learner code failure
