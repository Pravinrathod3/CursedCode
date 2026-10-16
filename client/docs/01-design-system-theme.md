# 01 — Design System & Theme

## Creative direction

Use a **JJK-inspired cursed-energy training arena** as inspiration, not a direct anime replica. The interface should feel intense and focused while remaining readable for long coding sessions.

### Mood words

- Dark, cinematic, disciplined
- Cursed-energy glow used sparingly
- Training ranks, seals, technique cards, domain-like focus mode
- Technical and functional, not cluttered

### Avoid

- Official anime logos, screenshots, character art, or copyrighted key visuals
- Overusing glow, gradients, animated particles, or red warning colors
- Making the editor low-contrast
- Using color alone to communicate a status

## Suggested color tokens

Use semantic CSS variables and adapt them to the current shadcn/ui theme setup.

| Token | Suggested direction | Usage |
|---|---|---|
| Background | near-black charcoal | app canvas |
| Surface | deep slate | cards, panels |
| Elevated surface | slightly lighter slate | popovers, menus |
| Primary | electric violet | primary actions, focus |
| Accent | cursed crimson | rare emphasis, active danger state |
| Secondary accent | cool cyan | selected metadata or progress |
| Text | warm white | primary text |
| Muted text | cool gray | secondary labels |
| Success | restrained green | passed tests |
| Warning | amber | caution or pending |
| Destructive | accessible red | runtime errors or destructive actions |
| Border | low-contrast slate | panel separation |

Do not hard-code these colors in every component. Create tokens so the theme can be tuned consistently.

## Typography

- Use a highly readable sans-serif for UI text.
- Use a monospace font for code and test output.
- Headings can be compact and bold; avoid excessive all-caps copy.
- Keep body text at a comfortable size and line height.
- Use clear labels such as “Wrong output” rather than cryptic abbreviations.

## Layout principles

- Desktop workspace: header/breadcrumbs, problem panel, editor, results/hints.
- Use resizable columns where practical; avoid tiny panes.
- Keep the primary “Run” and “Submit” actions easy to find.
- Use sticky headers only when they do not consume too much vertical space.
- On mobile, stack statement, editor, results, and hints vertically.

## Motion

- Short transitions for hover, tab changes, and panel expansion.
- Avoid looping animations while the learner is typing.
- Respect `prefers-reduced-motion`.
- Never use animation as the only feedback that a submission completed.

## shadcn/ui conventions

Use shadcn/ui primitives as the default rather than inventing every control. Recommended:
- `Breadcrumb` for navigation context
- `Button` for actions
- `Card` for challenge and progress surfaces
- `Badge` for difficulty and concept tags
- `Tabs` for Description / Submissions / Hints
- `Resizable` for the editor workspace, if available in the installed setup
- `ScrollArea` for long panels
- `Tooltip` for icon-only controls
- `Dialog` for confirmation or optional solution reveal
- `Accordion` for examples and hint steps
- `Progress` for concept mastery
- `Skeleton` for loading
- `Alert` for persistent errors
- `Sonner` toaster for brief action feedback

## Example visual language

- “Training Rank” = difficulty label
- “Cursed Technique” = optional concept label, not a replacement for the actual concept name
- “Domain Focus” = optional distraction-reduced editor mode
- “Weakness Pattern” = recurring mistake
- “Next Training” = recommended challenge

Keep ordinary educational terminology visible alongside any themed labels.
