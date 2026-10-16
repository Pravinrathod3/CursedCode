# rules.md — cursedCode UI rules

**Scope: frontend / UI only.** Backend, sandbox, judging, hints generation and learner-model rules live in a separate file (`backend_rules.md`). This file never overrides that one. Where the UI touches backend data, it only describes what to *display* and what to *never display*.

Every AI agent that writes UI code, styling or copy must read this file fully before each task. If a task conflicts with this file, this file wins. If this file is silent, ask the human; do not invent.

---

## 0. Summary

- **Product name:** `cursedCode` (exactly this casing, one word). Slug: `cursedcode`.
- **What the UI is:** a practice site where a beginner writes Python, runs it, sees per-test results, reads a plain explanation, reveals hints one at a time, and sees recurring mistakes and progress.
- **Theme:** Jujutsu Kaisen *visual mood* (dark, ink, glowing blue and violet, kanji watermarks, grade badges). It is fan-made.
- **Golden rule: someone who has never heard of Jujutsu Kaisen must be able to use every screen with zero confusion.** All labels use plain, standard words. The theme lives in colours, backdrops, badges and decoration, not in vocabulary.
- **Priority order:** (1) clarity and correctness, (2) never leaking hidden-test data, (3) accessibility, (4) theme.

---

## 1. UI non-negotiables

1. **Hidden tests show only the test number and the outcome.** Never render a hidden test's input, call, expected value, output or error text, in any form: text, tooltip, `title`, `aria-label`, `data-*` attribute, console log, or error toast.
2. **Render server text as plain text.** Explanations and hints are displayed as escaped text, never as HTML and never with markdown or code formatting. If a hint ever arrives containing a code fence or backticks, do not format it as code; display as-is and flag it in the console for the developer.
3. **Outcome names are exactly four:** `passed`, `wrong_output`, `runtime_error`, `timeout`. Display them as: **Passed**, **Wrong output**, **Runtime error**, **Timeout**. Never rename them.
4. **If a run was stopped by a resource limit, say which one** in plain words (for example "Runtime error: memory limit"), using the `limit` field when present.
5. **Never invent data.** If a field is missing, show a neutral empty state, not a made-up value.
6. **Colour is never the only signal.** Every status shows colour + icon + text.
7. **Accessibility floor:** text contrast WCAG AA, visible keyboard focus, all icons have text alternatives, `prefers-reduced-motion` respected.
8. **Footer on every page:** `Fan project. Not affiliated with or endorsed by the creators of Jujutsu Kaisen.`
9. **No official franchise art, character images, logos or stills.** Use only the files listed in section 8.
10. **Do not hit the hint endpoint in loops or auto-reveal hints.** One user click reveals one hint.

---

## 2. Naming: use standard words

### 2.1 Default names (use these, do not theme them)

| Concept | UI label |
|---|---|
| The code runner | **Run** (button text: `Run`, while running: `Running…`) |
| Visible tests | **Visible tests** |
| Hidden tests | **Hidden tests** |
| Sandbox | **Sandbox** |
| Challenge | **Challenge** (list page: **Challenges**) |
| Concept | **Concept** |
| Learner | **Learner** |
| Hint | **Hint** (button: `Get a hint`) |
| Explanation | **What went wrong** (section heading) |
| Recurring mistakes | **Recurring mistakes** |
| Mastery | **Mastery** |
| Next challenge | **Next challenge** |
| Progress page | **Progress** |
| Mistake tags | Display names in section 7 |

### 2.2 The only themed vocabulary: Grades

Grades use the official scale, lowest to highest:

`Grade 4` < `Grade 3` < `Grade 2` < `Semi-Grade 1` < `Grade 1` < `Special Grade`

- **Challenge difficulty:** easy = Grade 4, medium = Grade 3, hard = Grade 2.
- **Mastery display:** the backend gives a score from 0 to 1 per concept. Show it as a grade badge **and** the number. Never store the grade; derive it:

| Mastery score | Badge |
|---|---|
| 0.00 to < 0.20 | Grade 4 |
| 0.20 to < 0.40 | Grade 3 |
| 0.40 to < 0.60 | Grade 2 |
| 0.60 to < 0.80 | Semi-Grade 1 |
| 0.80 to < 0.93 | Grade 1 |
| 0.93 to 1.00 | Special Grade | 

Mastery Score will be added from backend.

- **Explain grades for newcomers.** Every grade badge has a tooltip and the Progress page has a one-line legend: `Grade 4 is the starting level. Special Grade is the highest.` Wherever a challenge shows a grade, it also shows the plain word (for example `Grade 4 · Easy`).

### 2.3 Decoration only (never carries meaning)

Kanji may appear as faint background decoration only: 呪 (curse) on the landing page. Never place kanji where the user needs to read it to understand something. Do not use character names or character-specific techniques anywhere.

---

## 3. Visual system

### 3.1 Colour tokens (define once as CSS custom properties in a single tokens file; use only these)

| Token | Hex | Use |
|---|---|---|
| `--color-bg` | `#08080D` | Page background |
| `--color-panel` | `#12121C` | Cards, editor, panels |
| `--color-text` | `#EDE8DC` | Primary text |
| `--color-muted` | `#9A9BB0` | Secondary text |
| `--color-accent-blue` | `#4DA3FF` | Buttons, links, focus ring |
| `--color-accent-violet` | `#9B5CFF` | Highlights, subtle glows |
| `--color-passed` | `#2EE6A8` | Passed (teal) |
| `--color-wrong-output` | `#F2B84B` | Wrong output (gold) |
| `--color-runtime-error` | `#E0243A` | Runtime error (red) |
| `--color-timeout` | `#B18CFF` | Timeout (violet) |

No new hex values in components. Red is reserved for Runtime error and error states.

Outcome colours: passed teal, wrong_output gold, runtime_error red, timeout violet. Always pair colour with an icon and a text label, because colour alone fails for colour-blind users. Every outcome carries an icon and a text label, never colour alone. Keep body text contrast at WCAG AA or better.

### 3.2 Typography

All fonts are free on Google Fonts:

| Role | Font | Notes |
|---|---|---|
| Display / titles | **Anton** or **Bebas Neue** | Tall, condensed, poster energy |
| Brush accent (sparingly) | **Yuji Boku** or **Permanent Marker** | Taglines and grade stamps only |
| Japanese ghost text | **Zen Antique** or **Shippori Mincho** | Decorative kanji, low opacity |
| Body / UI | **Inter** | Readable for long hint text |
| Code editor and tests | **JetBrains Mono** | With ligatures off for beginners |

Rule of thumb: never more than one display font and one brush font on a screen, and never set paragraphs in a display font.

- **Self-host all fonts** from `/assets/fonts/` (the demo may run offline). No runtime Google Fonts link.
- Type scale: 12 / 14 / 16 / 20 / 28 / 40 px. Nothing else.
- Fallback stacks: `system-ui, sans-serif` and `ui-monospace, monospace`. Use `font-display: swap`.

### 3.3 Spacing and shape

- Spacing scale: 4, 8, 12, 16, 24, 32, 48 px.
- Panels: 12px radius, 1px border at 12% white. No heavy shadows.
- Focus ring: 2px `--color-accent-blue`.

### 3.4 Backdrop

- All pages: dark gradient (`bg_void_gradient.svg`) plus tileable grain (`bg_grain.png`, about 6% opacity).
- Landing and Progress: halftone corner (`bg_halftone_corner.svg`) at low opacity.
- Landing only: skyline silhouette at the bottom and the ghost 呪 at about 5% opacity.
- **Challenge page (the main work screen): calm.** No decorative kanji, no animated background, nothing behind the editor that reduces readability.

### 3.5 Motion

| Effect | Where | Duration |
|---|---|---|
| Result fade-in | When test results arrive | 200 ms |
| Hint reveal | When a new hint appears | 250 ms |
| Run button spinner | While running | until done |

No glitch, shake, parallax or full-screen animations. Under `prefers-reduced-motion`, disable all of the above except the spinner, which becomes a static "Running…" label.

---

## 4. Screens and components

### 4.1 Screens and routes (build in this order)

1. **Challenge page** `/challenges/:challengeId` (highest judge value).
2. **Progress** `/progress`.
3. **Challenges list** `/challenges` (at least 10 challenges).
4. **Landing** `/`: product name, one-line tagline, learner-name field (a pseudonym, no real names), "Start" button, footer disclaimer.

Navigation bar: logo, `Challenges`, `Progress`. Nothing else.

### 4.2 Challenge page layout

- **Left:** title, grade badge with difficulty word, concept tags, description, code editor (starter code preloaded), **Run** button, sandbox status line.
- **Right:** Visible tests, Hidden tests, mistake tags, What went wrong, Hint control.
- Mobile: stack vertically, editor first.

### 4.3 Component specs

**Run button:** primary, accent-blue, text `Run`, icon `icon_run.svg`. Disabled while running (shows `Running…`). Never auto-run.

**Sandbox status line** (small, under the Run button):

| State | Copy |
|---|---|
| idle | `Sandbox ready` |
| running | `Running your code in the sandbox` |
| finished | `Run finished` |
| stopped by a limit | `Stopped: <time / memory / output / disk> limit reached` |

Only claim what the backend actually does. Do not add security promises in UI copy.

**Visible test row:** test number, `call`, `expected`, `got`, outcome icon + label. Mono font. 4px left stripe in the outcome colour.

**Hidden test row:** test number + outcome icon + label + the lock icon `icon_hidden_test.svg`. Nothing else. A line above the list says: `Hidden tests check cases you can't see. Their details stay private.`

**Summary line above the test lists:** `3 of 3 visible tests passed · 4 of 6 hidden tests passed`.

**Hint control:** a `Get a hint` button and four small dots or icons (`icon_hint_off.svg` / `icon_hint_on.svg`). Each click reveals the next hint and shows `Hint N of 4` (use the `level` and `remaining` values from the API; do not hard-code 4 if the API says otherwise). After the last hint the button is replaced by the copy in section 5. UI may *encourage* a retry before the first hint (`Try once more before a hint?` with a `Get a hint anyway` button) but must never block the click.

**Mistake chip:** icon + display name + one-line description (section 7).

**Mastery row:** concept name, grade badge, bar, numeric score (two decimals).

**Next challenge card:** challenge title, grade badge, and the reason text exactly as the API returns it.

**Recurring mistakes panel:** each recurring tag with its icon, description, and the list of challenges it appeared in. If none: `No recurring mistakes yet.`

---

## 5. Copy and tone

- Short, friendly, encouraging. Praise effort and reasoning. Never say "easy", "obvious" or "simply".
- Never claim the code is "correct" beyond the tests ("All tests passed" is fine).
- Never show or imply a full solution.

| Moment | Copy |
|---|---|
| Landing tagline | `Find the bug yourself. Get help only when you need it.` |
| All tests passed, no hints used | `All tests passed with no hints. Nice work.` |
| All tests passed, hints used | `All tests passed. Next time, try with one hint fewer.` |
| Some tests failed | `{n} of {m} tests failed. Read what went wrong, then try again.` |
| Last hint shown | `That's all the hints. You're closer than you think. Try another attempt.` |
| No attempts yet | `No attempts yet. Pick a challenge to begin.` |
| Run error from server | `Something went wrong running your code. Please try again.` |
| Footer | `Fan project. Not affiliated with or endorsed by the creators of Jujutsu Kaisen.` |

---

## 6. Data the UI consumes (display contract)

The UI only reads these fields. Request and response shapes are owned by `backend_rules.md`; if they differ, the backend file wins and this section must be updated.

**Submit result:** `submission_id`, `learner_id`, `challenge_id`, `visible[]` (`test`, `call`, `expected`, `got`, `outcome`), `hidden[]` (`test`, `outcome` only), `mistake_tags[]`, `explanation`, optional `limit`.

**Hint result:** `hint`, `level`, `remaining`.

**Learner record:** `recurring_mistakes[]` (`tag`, `challenges[]`), `mastery` (concept to 0..1), `next_challenge` (`challenge_id`, `reason`).

Rules:
- Ignore unknown fields. Never render fields the UI doesn't list here.
- If `hidden[]` items contain anything beyond `test` and `outcome`, **do not render the extras** and log a console warning.
- Outcome strings are looked up in one map (ID to label, icon, colour). Never string-match on free text.

---

## 7. Mistake tags: display names and descriptions

| Tag ID (from API) | Display name | Description shown to the learner | Icon |
|---|---|---|---|
| `off_by_one` | Off by one | Your loop or index stops one step too early or goes one step too far. | `mistake_off_by_one.svg` |
| `unhandled_short_input` | Short input not handled | Your code breaks, or gives a wrong answer, on empty or very short input. | `mistake_unhandled_short_input.svg` |
| `print_not_return` | Printed instead of returned | Your function prints a result instead of returning it. | `mistake_print_not_return.svg` |
| `boundary_comparison` | Boundary comparison | A comparison such as less-than versus less-than-or-equal is off at the exact boundary value. | `mistake_boundary_comparison.svg` |
| `mutates_input` | Changes the input | Your function changes the list it was given. | `mistake_mutates_input.svg` |
| `syntax_or_name_error` | Syntax or name error | Python could not run your code because of a typo, a missing colon, or a name that doesn't exist. | `mistake_syntax_or_name_error.svg` |
| `infinite_loop` | Runs too long | Your code kept running until time ran out. | `mistake_infinite_loop.svg` |
| `hardcoded_values` | Hard-coded values | Your code passes the examples but looks tailored to them rather than the general rule. | `mistake_hardcoded_values.svg` |
| `other_logic_error` | Logic error | Something in the logic is off. Use the explanation and hints to narrow it down. | `mistake_other_logic_error.svg` |

If the API returns a tag ID not in this table, show it as plain text with a generic icon (`mistake_other_logic_error.svg`) and do not crash.

---

## 8. Assets: location, naming and usage

### 8.1 Rules

- Folder: `frontend/public/assets/`. Reference at runtime as `/assets/<category>/<filename>`.
- Filenames are **lowercase snake_case**: `<category>_<name>.<ext>`. No spaces, hyphens or camelCase.
- **Outcome and mistake icons use the exact API IDs in their filenames**, so the path is computed: `/assets/icons/outcome_<outcome>.svg` and `/assets/mistakes/mistake_<tag>.svg`.
- Vector assets are `.svg` and use `currentColor` where recolouring is needed.
- **Never** invent a filename not listed here. **Never** hotlink assets or fonts.
- **If a listed file is missing,** do not fail: use the fallback in the table and append the missing filename to `frontend/public/assets/MISSING_ASSETS.md`. Do not create placeholder files with real names.

### 8.2 Brand (`/assets/brand/`)

| File | Spec | Fallback |
|---|---|---|
| `brand_logo_wordmark.png` / `logo.png` | Stylized JJK blood-red brush "CursëdCödë" wordmark (1018×261 PNG) | Text "cursedCode" in Anton |
| `brand_logo_wordmark.svg` | "cursedCode" wordmark, about 600×120 viewBox | Text "cursedCode" in Anton |
| `brand_logo_mark.svg` | Square symbol, 128×128 viewBox | Hide |
| `brand_favicon.svg` | 32×32 viewBox | Use the logo mark |
| `brand_favicon_32.png` | 32×32 PNG | Omit |
| `brand_apple_touch_icon.png` | 180×180 PNG | Omit |
| `brand_og_image.png` | 1200×630 PNG | Omit |

### 8.3 Backdrops (`/assets/backdrops/`)

| File | Spec | Used on | Fallback |
|---|---|---|---|
| `bg_void_gradient.svg` | Vertical gradient `#08080D` to `#1A1033` | All pages | CSS gradient from tokens |
| `bg_grain.png` | 256×256 tileable noise, transparent | All pages, about 6% opacity | Omit |
| `bg_halftone_corner.svg` | Halftone dots, top-right, 480×480 viewBox | Landing, Progress | Omit |
| `bg_landing_skyline.svg` | Dark city + torii silhouette, 1600×300 viewBox | Landing footer only | Omit |

### 8.4 Kanji decoration (`/assets/kanji/`)

| File | Content | Used on | Fallback |
|---|---|---|---|
| `kanji_curse.svg` | 呪, large, single colour | Landing watermark | Text in Zen Antique |

### 8.5 Grade badges (`/assets/badges/`, 96×96 viewBox, legible at 32px)

| File | Grade |
|---|---|
| `grade_4.svg` | Grade 4 |
| `grade_3.svg` | Grade 3 |
| `grade_2.svg` | Grade 2 |
| `grade_semi_1.svg` | Semi-Grade 1 |
| `grade_1.svg` | Grade 1 |
| `grade_special.svg` | Special Grade |

Fallback for any badge: a rounded square with the grade text in Anton.

### 8.6 Icons (`/assets/icons/`, 24×24 viewBox, `currentColor`)

| File | Use |
|---|---|
| `outcome_passed.svg` | Passed |
| `outcome_wrong_output.svg` | Wrong output |
| `outcome_runtime_error.svg` | Runtime error |
| `outcome_timeout.svg` | Timeout |
| `icon_hidden_test.svg` | Hidden test rows (lock) |
| `icon_sandbox.svg` | Sandbox status line |
| `icon_hint_off.svg` | Unrevealed hint dot |
| `icon_hint_on.svg` | Revealed hint dot |
| `icon_run.svg` | Run button |
| `icon_challenges.svg` | Nav: Challenges |
| `icon_progress.svg` | Nav: Progress |
| `icon_next_challenge.svg` | Next challenge card |
| `icon_recurring_mistake.svg` | Recurring mistakes panel heading |

Fallback for outcome icons: text glyphs. The text label is always shown beside the icon.

### 8.7 Mistake icons (`/assets/mistakes/`, 24×24 viewBox, `currentColor`)

Exactly the nine files named in section 7: `mistake_off_by_one.svg`, `mistake_unhandled_short_input.svg`, `mistake_print_not_return.svg`, `mistake_boundary_comparison.svg`, `mistake_mutates_input.svg`, `mistake_syntax_or_name_error.svg`, `mistake_infinite_loop.svg`, `mistake_hardcoded_values.svg`, `mistake_other_logic_error.svg`.

### 8.8 Fonts (`/assets/fonts/`, WOFF2, SIL OFL)

| File | Font |
|---|---|
| `font_anton_regular.woff2` / `font_bebas_neue.woff2` | Anton Regular / Bebas Neue (Display) |
| `font_yuji_boku.woff2` / `font_permanent_marker.woff2` | Yuji Boku / Permanent Marker (Brush accent) |
| `font_zen_antique_regular.woff2` / `font_shippori_mincho.woff2` | Zen Antique Regular / Shippori Mincho (Ghost kanji) |
| `font_inter_variable.woff2` | Inter (variable, Body/UI) |
| `font_jetbrains_mono_variable.woff2` | JetBrains Mono (variable, Code/Tests) |

### 8.9 Complete tree

```
frontend/public/assets/
  MISSING_ASSETS.md
  brand/       6 files
  backdrops/   4 files
  kanji/       1 file
  badges/      6 files
  icons/      13 files
  mistakes/    9 files
  fonts/       4 files
```

Total: 43 files. Every one has a fallback, so UI development never waits on assets.

---

## 9. Engineering conventions (UI)

- Keep one tokens file for colours, spacing and type scale. Components read tokens only.
- Keep one `outcomeMap` (ID to label, icon path, colour token) and one `mistakeMap` (ID to display name, description, icon path). All components use these maps.
- Keep one `gradeFromScore` helper implementing the table in section 2.2.
- Keep user-facing strings in one strings file so copy changes don't touch components.
- Do not add UI libraries, fonts or icon packs without asking the human.
- The UI must work when the backend returns an error: show the generic error copy, never a stack trace.

---

## 10. Pre-finish checklist (run before declaring any UI task done)

- [ ] No hidden-test detail is rendered or present in the DOM, attributes or logs
- [ ] Server text is rendered as plain escaped text
- [ ] Outcome labels are exactly Passed / Wrong output / Runtime error / Timeout, with icon + colour + text
- [ ] Standard names used (Run, Visible tests, Hidden tests, Sandbox, Hint, Challenge, Progress); no extra themed vocabulary
- [ ] Grades shown with plain-word difficulty and a tooltip or legend
- [ ] Only colour, font and spacing tokens from section 3 are used
- [ ] Every asset path matches section 8; missing ones use fallbacks and are logged
- [ ] Contrast, focus rings, alt text and reduced-motion are handled
- [ ] Footer disclaimer is on every page
- [ ] A first-time visitor who doesn't know the franchise could use the screen unaided
