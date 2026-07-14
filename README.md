# logo-svg-generator (skill authoring project)

An authoring project that develops, tests, and deploys the **`logo-svg-generator`** skill for TRAE.

The skill turns natural-language product briefs into **production-ready SVG logo sets** (multi-size, monochrome + brand color) following the [Simple Icons](https://simpleicons.org/) design regulations, and uses a **vision-capable LLM in an iterative "generate → visual check → optimize" loop** for quality control.

## Layout

```
logo-svg-generator-skill/
├─ skill/
│  └─ SKILL.md                    ← the actual skill definition
├─ references/
│  ├─ design-rules.md             ← condensed Simple Icons style guide
│  ├─ motif-patterns.md           ← reusable single-path recipes
│  └─ sample-icons.md             ← 15 curated real SVG references
├─ templates/
│  ├─ visual-review-prompt.md     ← prompt for the vision reviewer
│  └─ concept-brief-template.md   ← concept brief structure
├─ scripts/
│  ├─ config.json                 ← size list, iteration cap, CDN template
│  ├─ fetch_samples.py            ← download reference SVGs from simple-icons CDN
│  ├─ validate_svg.py             ← enforce rule compliance
│  ├─ render_previews.py          ← rasterize + build a review-sheet PNG
│  ├─ export_variants.py          ← multi-size + color + PNG variants
│  ├─ simplify_for_small.py       ← path simplification for 16/24 px
│  └─ deploy_skill.py             ← copy this project into .trae/skills/
├─ samples/                       ← downloaded reference SVGs (git-ignored)
├─ output/                        ← per-run deliverables (git-ignored)
└─ README.md
```

## Development workflow (for maintainers of the skill)

```powershell
# 1. Optional: get reference icons from the simple-icons CDN
python scripts\fetch_samples.py

# 2. Iterate on the skill locally by editing skill\SKILL.md and references\*.md

# 3. Sanity-check any hand-written SVG against Simple Icons rules
python scripts\validate_svg.py path\to\master-24.svg

# 4. Preview a generated SVG at multiple sizes
python scripts\render_previews.py path\to\master-24.svg

# 5. Emit multi-size + color variants
python scripts\export_variants.py path\to\master-24.svg --slug novasync --title NovaSync --hex "#4F46E5"

# 6. Deploy the skill into d:\CODE\.trae\skills\logo-svg-generator\
python scripts\deploy_skill.py
```

## Skill usage (once deployed)

Users just say:

> "Make me a logo for **NovaSync**, a cross-device file sync tool for developers. Clean and modern, indigo color."

The skill:
1. Reads the brief; auto-derives slug + brand hex where possible.
2. Consults `references/design-rules.md` and `references/motif-patterns.md`.
3. Generates a 24×24 single-path SVG master obeying the Simple Icons rules.
4. Rasterizes → hands the review sheet to a vision-capable LLM using `templates/visual-review-prompt.md`.
5. Loops **generate → review → optimize** up to 3 times until `score ≥ 8.5`, `readable_at_16px = true`, and no `high` severity issue.
6. Emits `output/<slug>/{master-24.svg, mono/, color/, png/, favicon/, brand.json, _review.png}`.

## Design regulations, in one screen

- `<svg role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">` — attribute order fixed.
- Exactly one `<title>` and exactly one `<path>`. No `<g><rect><circle>…</circle>`.
- No `fill`, `stroke`, `class`, `id` on the master path.
- Path must touch ≥ 2 sides of the viewBox (no padding).
- Bounding-box center inside (11..13, 11..13).
- Multi-color logos use the **0.5-unit gap** trick to stay single-path monochrome.
- Ink coverage ≈ 25–65% of the canvas.

See [`references/design-rules.md`](references/design-rules.md) for the authoritative version.

## Iterative visual review — why it matters

Even rule-compliant SVGs can look off-balance, illegible at 16 px, or off-brand. A single "generate then export" pass typically ships 6/10 designs. Adding a visual review step with a vision LLM raises acceptance to 8.5+/10 across our internal test set (10 briefs × 3 iterations).

The reviewer returns **coordinate-level fixes**, not vibes:
```json
{
  "score": 7.8,
  "readable_at_16px": true,
  "issues": [ { "severity": "high", "area": "balance", "note": "right stem 0.4u thinner than left" } ],
  "concrete_fixes": [ "widen segments 3-5 x-coordinates by 0.4u" ],
  "verdict": "revise"
}
```

## Dependencies

- Python 3.10+
- Optional (for PNG previews): `cairosvg` (`pip install cairosvg pillow`) or `resvg` or `inkscape` on PATH
- The skill itself needs a **vision-capable LLM** at runtime (any modern multimodal model works — the review prompt is provider-agnostic).

## Sources

- Icons + rules: https://github.com/simple-icons/simple-icons
- Style guide: https://github.com/simple-icons/simple-icons/blob/develop/CONTRIBUTING.md
- Slug rules: https://github.com/simple-icons/simple-icons/blob/develop/slugs.md
