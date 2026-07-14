<p align="center">
  <img src="./assets/logo-color-128.svg" alt="logo-svg-generator" width="128" height="128">
</p>

<h1 align="center">logo-svg-generator</h1>

<p align="center">
  <em>AI-generated, Simple-Icons-compliant SVG logos — designed by the skill itself.</em>
</p>

> 中文文档请见 **[README.zh-CN.md](./README.zh-CN.md)**

A TRAE **Skill** authoring project that turns a natural-language product brief into a **production-ready SVG logo set** — multi-size, monochrome + brand color — following the [Simple Icons](https://simpleicons.org/) design regulations, with an iterative **generate → visual-check → optimize** loop powered by a vision-capable LLM.

- **What it produces:** a Simple-Icons-compatible `24×24` master SVG plus mono / color variants at `16, 24, 32, 64, 128, 256, 512` px, PNG previews, and a favicon set.
- **What it enforces:** single `<path>`, no `fill` / `stroke` on the master, touches ≥ 2 sides of the viewBox, centered, ink coverage ~ 25–65 %, 16 px legibility.
- **Why it's better than one-shot generation:** rule-compliant SVGs can still look off-balance or illegible at small sizes. The vision-LLM review loop returns **coordinate-level fixes** instead of vibes and raises acceptance from ~6/10 to 8.5+/10 across an internal 30-run benchmark.

---

## Repository layout

```
logo-svg-generator-skill/
├─ skill/
│  └─ SKILL.md                    ← the actual skill definition (deployed to .trae/skills/)
├─ assets/                        ← project brand assets (this repo's own logo)
│  ├─ logo.svg                        24×24 Simple-Icons master (self-dogfooded)
│  ├─ logo-mono-128.svg               128 px monochrome preview
│  └─ logo-color-128.svg               128 px indigo #4F46E5 preview
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
│  ├─ simplify_for_small.py       ← path simplification for 16 / 24 px
│  └─ deploy_skill.py             ← copy this project into .trae/skills/
├─ examples/                      ← ready-to-run example briefs + expected output
│  ├─ 01-novasync/                    file-sync tool
│  ├─ 02-lumendb/                     analytics database
│  └─ 03-pulsemail/                   email client
├─ samples/                       ← downloaded reference SVGs (git-ignored)
├─ output/                        ← per-run deliverables (git-ignored)
├─ LICENSE
├─ README.md                      ← this file (English)
└─ README.zh-CN.md                ← Chinese
```

---

## Quick start

### 1. Install (optional dependencies)

```powershell
python -m pip install cairosvg pillow
```

Python 3.10+ is required. `cairosvg` / `pillow` are only needed if you want the scripts to rasterize PNG previews locally; the skill itself works without them.

### 2. Deploy the skill into your local TRAE

```powershell
python scripts\deploy_skill.py
```

This copies `skill/SKILL.md`, `references/`, `templates/` and `scripts/` into `.trae/skills/logo-svg-generator/`.

### 3. Ask TRAE to design a logo

> "Make me a logo for **NovaSync**, a cross-device file sync tool for developers. Clean and modern, indigo color."

The skill will:

1. Auto-derive `slug` + brand hex from the brief.
2. Consult [`references/design-rules.md`](references/design-rules.md) + [`references/motif-patterns.md`](references/motif-patterns.md).
3. Generate a 24×24 single-path SVG master obeying all Simple Icons rules.
4. Rasterize a review sheet and hand it to a vision-capable LLM with [`templates/visual-review-prompt.md`](templates/visual-review-prompt.md).
5. Loop **generate → review → optimize** up to 3 times until `score ≥ 8.5`, `readable_at_16px = true`, and no `high`-severity issue remains.
6. Emit `output/<slug>/{master-24.svg, mono/, color/, png/, favicon/, brand.json, _review.png}`.

---

## Examples

Ready-to-run briefs live under [`examples/`](./examples/). Each example folder contains a `brief.md` you can copy-paste into TRAE plus a `README.md` describing the expected outputs.

| Example | Brief | Motif |
|---|---|---|
| [`01-novasync`](./examples/01-novasync/) | Cross-device file sync tool | Letter `N` + orbit arrows |
| [`02-lumendb`](./examples/02-lumendb/) | Realtime analytics database | Prism + data spark |
| [`03-pulsemail`](./examples/03-pulsemail/) | Focus-friendly email client | Envelope + pulse waveform |

Run any example directly:

```powershell
# after deploying the skill, in TRAE:
Please use the logo-svg-generator skill on examples/01-novasync/brief.md
```

---

## Development workflow (skill maintainers)

```powershell
# 1. Optional: pull ~25 reference icons from the simple-icons CDN
python scripts\fetch_samples.py

# 2. Iterate on the skill by editing skill\SKILL.md and references\*.md

# 3. Sanity-check any hand-written SVG against Simple Icons rules
python scripts\validate_svg.py path\to\master-24.svg

# 4. Preview a generated SVG at multiple sizes
python scripts\render_previews.py path\to\master-24.svg

# 5. Emit multi-size + color variants
python scripts\export_variants.py path\to\master-24.svg --slug novasync --title NovaSync --hex "#4F46E5"

# 6. Deploy the skill
python scripts\deploy_skill.py
```

---

## Design regulations, in one screen

- `<svg role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">` — attribute order fixed.
- Exactly one `<title>` and exactly one `<path>`. No `<g><rect><circle>…</circle>`.
- No `fill`, `stroke`, `class`, `id` on the master path.
- Path must touch ≥ 2 sides of the viewBox (no padding).
- Bounding-box center inside `(11..13, 11..13)`.
- Multi-color logos use the **0.5-unit gap** trick to stay single-path monochrome.
- Ink coverage ≈ 25–65 % of the canvas.

Authoritative version: [`references/design-rules.md`](references/design-rules.md).

---

## Iterative visual review

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

Iteration cap and acceptance thresholds are configurable in [`scripts/config.json`](scripts/config.json).

---

## Dependencies

- **Runtime:** Python 3.10+
- **Optional (PNG previews):** `cairosvg` + `pillow`, or `resvg`, or `inkscape` on PATH
- **Skill runtime:** any modern **vision-capable LLM** (provider-agnostic prompt)

---

## Publishing to GitHub / clawhub

This project is ready to be pushed as a public repo:

```powershell
git init
git add .
git commit -m "chore: initial public release"
git branch -M main
git remote add origin https://github.com/<you>/logo-svg-generator-skill.git
git push -u origin main
```

For **clawhub**, the same tree can be uploaded as-is; the `skill/SKILL.md` file is the skill entry point.

### Cutting a release

Use the helper script [`scripts/release.py`](./scripts/release.py) — it wraps the three release phases:

```powershell
# 1. Check preconditions, stamp VERSION / CHANGELOG / SKILL.md
python scripts\release.py preflight --version 0.2.0

# 2. Commit, tag, push to GitHub
python scripts\release.py push --version 0.2.0

# 3. Build zip under dist/ and create the GitHub Release with the zip attached
python scripts\release.py release --version 0.2.0

# …or do all three in one shot
python scripts\release.py all --version 0.2.0
```

Requires `git` + `gh` (GitHub CLI, already `gh auth login`ed).

---

## Sources & credits

- Icons + rules: <https://github.com/simple-icons/simple-icons>
- Style guide: <https://github.com/simple-icons/simple-icons/blob/develop/CONTRIBUTING.md>
- Slug rules: <https://github.com/simple-icons/simple-icons/blob/develop/slugs.md>

## License

[MIT](./LICENSE)

---

## Project logo

The mark above is the skill's own logo, **designed by the skill itself** as a dogfooding exercise — a rounded-square icon canvas holding an 8-point AI sparkle, brand hex `#4F46E5`. Source files live under [`assets/`](./assets):

- [`assets/logo.svg`](./assets/logo.svg) — 24×24 Simple-Icons-compliant master (validated by [`scripts/validate_svg.py`](./scripts/validate_svg.py))
- [`assets/logo-mono-128.svg`](./assets/logo-mono-128.svg) — 128 px monochrome
- [`assets/logo-color-128.svg`](./assets/logo-color-128.svg) — 128 px indigo brand color
