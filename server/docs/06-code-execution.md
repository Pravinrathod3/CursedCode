# 06 — Restricted Code Execution

## Goal

Execute untrusted learner code without allowing it to compromise the API server, database, secrets, or other learners.

## Recommended boundary

FastAPI should call a dedicated runner service. Do not use `exec`, `eval`, or an unrestricted local subprocess in the API process to run submissions.

Possible choices:
- A properly configured self-hosted Judge0 deployment
- Another isolated execution service with equivalent controls
- A tightly controlled OS/container sandbox built and reviewed by someone who understands its threat model

Do not assume a public demo endpoint is stable, free, or suitable for hostile code. Verify provider limits and judging requirements.

## Required controls

Configure and test:
- Wall-clock timeout
- CPU limit
- Memory limit
- Output limit
- Process count limit where supported
- Filesystem isolation and temporary workspace
- Network disabled
- Non-root user / least privilege
- No host mounts containing secrets
- Cleanup after every execution
- Runner concurrency limits
- Safe handling of runner crashes

A container alone is not automatically a secure sandbox; its privileges, mounts, namespaces, network, capabilities, and resource limits matter.

## Runner adapter

Keep vendor-specific API details behind a service interface, for example:
- `execute_submission(code, challenge, tests) -> execution_result`
- Normalize vendor-specific status values into the platform's outcome model.
- Validate the response schema and cap output sizes.
- Reject malformed or incomplete runner results.

## Timeouts and limits

- If the learner's program exceeds its execution time, report `timeout`.
- If it is killed due to memory/output/process limits, map it to `runtime_error` with a safe limit description when available.
- If the runner service itself is unreachable, return an infrastructure error to the API caller; do not label the learner's code as a runtime error.
- Never assume a missing result means passed.

## Hidden tests

Prefer the runner contract to return only outcome status for hidden tests. If the runner requires hidden test inputs, they must be transferred over a trusted channel and never returned to the client or sent to the LLM.

## Red-team tests

Try programs that:
- Loop forever
- Print huge output
- Allocate excessive memory
- Spawn child processes
- Attempt filesystem reads
- Attempt network access
- Try to read environment variables
- Raise exceptions containing input data
- Produce malformed or unexpected output

A successful test means the attempt is contained, no hidden data leaks, the API remains healthy, and a subsequent normal submission still runs.
