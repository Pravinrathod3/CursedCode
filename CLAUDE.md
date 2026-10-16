# Project Rules (apply to ALL work)

Frontend-specific rules: `frontend/CLAUDE.md`
Backend-specific rules: `backend/CLAUDE.md`

Read these before making any change. If a rule conflicts with a request, ask the user instead of silently breaking the rule.

## 1. Do not create random or throwaway files
- Never create scratch, demo, or temporary files (e.g. `test.js`, `temp.py`, `example.tsx`, `debug.ts`, `output.txt`).
- Only add tests when the user asks, and only inside the project's existing test folder using the existing test framework.
- Do not create extra docs, READMEs, or summary files unless asked.
- If you must create a temporary file to investigate something, delete it before finishing.
- Prefer editing an existing file over creating a new one.

## 2. Follow the existing structure and tech stack
- Before writing code, read the surrounding files and match their patterns, naming, folder layout, and style.
- Use only the libraries and frameworks already in the project. Do not add a new dependency, tool, or framework without asking first.
- Place new files in the folder that already holds similar files. Do not invent new top-level folders.
- Do not refactor, rename, or reformat unrelated code.
- Follow the existing linter, formatter, and TypeScript/type settings. Do not change their config.

## 3. Production-grade code quality
- Code must be readable, typed (where the language supports it), and consistently named.
- Handle errors and edge cases explicitly: loading, empty, failure, and invalid-input states.
- Validate all external input (user input, API responses, env variables).
- Never hardcode secrets, keys, URLs, or credentials. Use environment variables. Never read, edit, or commit `.env` files.
- Leave no `console.log`, commented-out code, unused imports, unused variables, or TODOs behind.
- Keep functions small and single-purpose. Use clear names instead of explaining with comments.
- Write comments only for non-obvious "why" decisions.

## 4. Reusability and no redundancy
- Before writing any component, function, hook, type, or constant, search the codebase for an existing one. Reuse or extend it.
- Do not copy and paste logic. If the same code would appear twice, extract it into a shared location.
- Build small, composable, single-responsibility units. Avoid large files that do many things.
- Keep shared code in the project's existing shared folders (utils, components/ui, lib, services, etc.).
- Magic numbers and repeated strings go into named constants.

## Before saying a task is done
1. Run the project's lint, type-check, and build commands (listed in the frontend/backend files) and fix every error you introduced.
2. Confirm no temporary or unused files remain.
3. Confirm no new dependency was added without approval.
4. Summarize what you changed and which existing code you reused.
