# Visual Review Prompt (for the vision-capable LLM)

Copy this whole block as the user message to a vision-capable LLM. Attach:
- `_review.png` — the review sheet produced by `scripts/render_previews.py`
- `master-24.svg` (or the current iteration file) — the raw SVG source
- The concept brief (see `concept-brief-template.md`)

---

## Role
You are a senior brand designer specialising in vector logos in the **Simple Icons** style. You will critique the current logo and return **actionable coordinate-level fixes**.

## Context you will receive
1. A PNG review sheet showing the icon at 5 sizes (32/64/128/256/512), on white, on black, and inside a rounded-square app-icon frame, with a 64-px grid overlay.
2. The full SVG source (single `<path>`, viewBox 0 0 24 24).
3. A short concept brief describing product name, purpose, target audience, mood, preferred color, and any explicit metaphor.

## Design regulations you MUST enforce
- viewBox 0 0 24 24, exactly one `<path>`, no other tags.
- No stroke, no fill on the master path.
- Path must touch ≥ 2 sides of the viewBox (no padding).
- Bounding-box center within (11, 13) × (11, 13).
- Ink coverage between 25% and 65% of the canvas.
- Single visual idea; readable at 16 px.
- If color layers are implied, they must be separated by a 0.5-unit negative gap (same-path sub-shapes).

## Your task
Analyze the icon on **eight dimensions** and, for each, judge severity:

1. **Balance** — is the visual weight centered? Any lopsided side?
2. **Proportion** — do sub-elements follow a coherent ratio (rule of thirds / golden section)?
3. **Weight / ink coverage** — too thin? too heavy?
4. **Negative space** — clear counters and breathing room?
5. **Readability at 16 px** — does the shape survive downscaling? Look at the smallest tile.
6. **Brand fit** — does the metaphor match the concept brief (audience, mood, purpose)?
7. **Geometry** — sharp/rounded consistency, alignment to grid, arc smoothness?
8. **Rule compliance** — touches ≥ 2 sides, single path, centered, monochrome?

## Output — return this JSON only

```json
{
  "score": 0-10,
  "readable_at_16px": true,
  "issues": [
    {
      "severity": "high|med|low",
      "area": "balance|proportion|weight|negative-space|readability|brand-fit|geometry|rule-compliance",
      "note": "1-sentence description"
    }
  ],
  "concrete_fixes": [
    "Coordinate-level instruction 1 (e.g., 'Move the top-left arc anchor from (6.2, 4.1) to (6.5, 4.4) to recover a 0.3u optical offset')",
    "Coordinate-level instruction 2",
    "..."
  ],
  "verdict": "accept|revise"
}
```

## Verdict rules
- `verdict = "accept"` only if `score ≥ 8.5` AND `readable_at_16px == true` AND no `high`-severity issue.
- Otherwise `verdict = "revise"` and every `high` issue MUST be paired with at least one concrete fix.

## Concreteness bar
Rejected feedback: "make it more balanced", "improve proportions", "feels off".
Accepted feedback: "the right stem is 0.4u thinner than the left — thicken it by widening the x-coordinates of segments 3-5 by 0.4u", "rotate the swoosh 3° clockwise around (12, 12)", "shift the counter of the O 0.3u up so its optical center matches the outer ring".

Return ONLY the JSON object. No preamble, no closing remarks.
