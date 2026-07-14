---
name: "logo-svg-generator"
description: "Generate multi-size SVG logos from natural-language product briefs, following Simple Icons design rules; runs an iterative generate → visual-check → optimize loop with a vision-capable LLM. Invoke when the user asks to design a logo, brand mark, app icon or product icon from a description."
---

# Logo SVG Generator

Turn a natural-language product brief (name, purpose, audience, mood, colors) into a **production-ready set of monochrome / brand-color SVG logos** in multiple sizes (16, 24, 32, 64, 128, 256, 512 px + 24×24 Simple-Icons-compatible master), by following the design regulations mined from the [Simple Icons](https://simpleicons.org/) project.

The skill uses an **iterative visual-review loop**: generate → rasterize → visually inspect (vision LLM) → critique → optimize → re-inspect → finalize.

---

## When to invoke

Trigger this skill whenever the user says any of:

- "Design / make / create a logo for …"
- "I need an SVG icon / brand mark / product logo for …"
- "Generate a logo for my product …"
- "帮我设计 / 生成一个 logo / 图标"
- "给我做一个 SVG 的品牌标识"

Do **NOT** invoke for: free-form illustration, complex marketing artwork, photo editing, or non-vector deliverables.

---

## Inputs the skill collects (or infers)

Before generation, gather (asking the user only when critical, otherwise infer sensibly):

| Field | Example |
|---|---|
| `product_name` | "NovaSync" |
| `product_purpose` | "cross-device file sync tool" |
| `audience / vibe` | "developers, minimal, techy" |
| `preferred_color` (hex) | `#4F46E5` (if omitted → pick from mood) |
| `mono_or_color` | monochrome + branded variant (default: both) |
| `sizes` | `[16, 24, 32, 64, 128, 256, 512]` (default) |
| `metaphor_hints` | "letter N + sync arrows" (optional) |

---

## Core workflow (MUST follow in order)

### Step 1 — Read the design regulations
Load **[references/design-rules.md](references/design-rules.md)** — the condensed Simple Icons style guide (viewBox 0 0 24 24, single `<path>`, no stroke, no fill attribute in master, touches ≥ 2 sides of viewBox, centered, single-color-with-0.5px-gap technique, slug rules).

Also skim **[references/motif-patterns.md](references/motif-patterns.md)** for common shape recipes (roundel, letterform, monogram, arrow, waveform, chevron, gear, chat-bubble, spark, etc.) with real path-fragment examples.

### Step 2 — Brainstorm 2–3 concept directions
Given the brief, write a short internal design brief covering:
1. **Metaphor** (what visual idea encapsulates the product?)
2. **Shape family** (geometric / letterform / abstract / pictogram)
3. **Color** (primary hex + when mono is required)
4. **Composition** (single symbol vs. mark + wordmark — this skill outputs **symbol only**, no wordmark)

Pick the strongest concept unless the user explicitly wants alternatives.

### Step 3 — Generate the 24×24 master SVG
Follow these hard rules (from Simple Icons CONTRIBUTING.md):

- Root: `<svg role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">`
- One `<title>` with the product name
- **Exactly one** `<path d="…"/>`
- **No** `<rect> <circle> <ellipse> <polygon> <g> <line> <defs> <style> <use> <mask> <clipPath>`
- **No** `fill` / `stroke` / `class` / `id` on the path (color is added later per variant)
- Path must **touch at least 2 sides** of the viewBox (no padding)
- Visual center around (12, 12); keep coordinates to ≤ 3 decimals
- Where color layers would exist, use a **0.5-unit gap** trick to imply separation while staying single-path

Write the master to `output/<slug>/master-24.svg`.

### Step 4 — Rasterize + visual check (VISION LLM REQUIRED)

Run `scripts/render_previews.py` to rasterize the master at **32, 64, 128, 256, 512** and produce a review sheet PNG (`output/<slug>/_review.png`) with:

- The icon on white, on black, and inside a rounded-square app-icon frame
- The 5 sizes side-by-side (to catch scale-dependent issues)
- Coordinate grid overlay at 64px

Then, hand `_review.png` **plus** the source SVG to a **vision-capable LLM** with the prompt in **[templates/visual-review-prompt.md](templates/visual-review-prompt.md)**. The reviewer must return a JSON critique:

```json
{
  "score": 0-10,
  "readable_at_16px": true,
  "issues": [
    {"severity": "high|med|low", "area": "balance|proportion|weight|negative-space|readability|brand-fit|geometry", "note": "…"}
  ],
  "concrete_fixes": ["Nudge the top-left arc 0.3u down", "Increase counter of letter N by 8% ..."],
  "verdict": "accept|revise"
}
```

### Step 5 — Optimize
If `verdict == "revise"`, apply the `concrete_fixes` to the SVG path (edit coordinates directly; keep single-path rule). Save as `master-24.v{N}.svg`, then **loop back to Step 4**.

- Max loop count: **3 iterations** (config in `scripts/config.json`).
- Stop early when `score ≥ 8.5` AND `readable_at_16px == true` AND no `high` severity issue remains.
- If loops exhaust without acceptance, keep the highest-scoring version and report the residual issues to the user.

### Step 6 — Generate multi-size + color variants
Once the master is accepted, run `scripts/export_variants.py` to produce:

```
output/<slug>/
├─ master-24.svg              (canonical Simple-Icons-compatible)
├─ mono/
│  ├─ logo-16.svg  logo-24.svg  logo-32.svg  logo-64.svg
│  ├─ logo-128.svg logo-256.svg logo-512.svg
├─ color/
│  └─ (same set, path filled with brand hex)
├─ png/
│  └─ logo-16.png … logo-512.png  (PNG previews)
├─ favicon/
│  └─ favicon.ico  apple-touch-icon-180.png
├─ _review.png
└─ brand.json                 ({ slug, title, hex, source_brief, iterations })
```

Multi-size SVGs are the **same path** with adjusted `width`/`height` attributes and (for small sizes 16 & 24) optional **path-simplification** (see `scripts/simplify_for_small.py`) — remove sub-details that vanish below 20px.

### Step 7 — Deliver
Give the user computer:// links to the top-level output folder, the master SVG, and the review sheet. Summarize the concept in ≤ 3 sentences.

---

## Non-negotiable design rules (quick check before finalizing)

Every SVG file the skill emits must pass **all** of:

- [ ] `role="img"`, `viewBox="0 0 24 24"`, `xmlns` — in that order
- [ ] Exactly one `<title>`
- [ ] Exactly one `<path>`, no other tags
- [ ] Master has no `fill`, no `stroke`, no `class`, no `id`
- [ ] Path touches ≥ 2 sides of the 24×24 canvas
- [ ] Visually centered (bounding box center within (11, 13) × (11, 13))
- [ ] Aspect ratio of original concept preserved (never stretched)
- [ ] Slug follows `slugify` rules (lowercase alphanumeric; `.`→`dot`, `+`→`plus`, `&`→`and`, remove spaces / punctuation)
- [ ] At 16 px it is still recognisable (validated by vision LLM)

---

## File layout of this skill project

```
logo-svg-generator-skill/
├─ skill/SKILL.md               ← this file (deployed to .trae/skills/)
├─ references/
│  ├─ design-rules.md          ← condensed Simple Icons rules
│  ├─ motif-patterns.md        ← common shape recipes + path snippets
│  └─ sample-icons.md          ← 15 curated real SVG references
├─ templates/
│  ├─ visual-review-prompt.md  ← prompt for vision LLM critique
│  └─ concept-brief-template.md
├─ scripts/
│  ├─ fetch_samples.py         ← pull N icons from simple-icons CDN
│  ├─ render_previews.py       ← SVG → review PNG sheet
│  ├─ export_variants.py       ← multi-size + color variants
│  ├─ simplify_for_small.py    ← small-size path simplification
│  ├─ validate_svg.py          ← rule compliance checker
│  ├─ deploy_skill.py          ← copy skill/ → .trae/skills/
│  └─ config.json
├─ samples/                    ← downloaded reference SVGs (git-ignored)
├─ output/                     ← per-run deliverables (git-ignored)
└─ README.md
```

---

## Related references

- [references/design-rules.md](references/design-rules.md)
- [references/motif-patterns.md](references/motif-patterns.md)
- [references/sample-icons.md](references/sample-icons.md)
- [templates/visual-review-prompt.md](templates/visual-review-prompt.md)
- [templates/concept-brief-template.md](templates/concept-brief-template.md)

Source of truth for design regulations:
- https://simpleicons.org
- https://github.com/simple-icons/simple-icons/blob/develop/CONTRIBUTING.md
- https://github.com/simple-icons/simple-icons/blob/develop/slugs.md
