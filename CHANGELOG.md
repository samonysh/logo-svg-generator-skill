# Changelog

All notable changes to **logo-svg-generator** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.1] - 2026-07-14
### Changed
- **Vision-capable LLM is now the default, non-optional reviewer for the logo check loop.** Step 4 in `SKILL.md` upgraded to a hard requirement: the `_review.png` MUST be attached as a real image input so the model exercises its vision pathway; text-only critique is not an acceptable substitute.
- When no vision-capable LLM is available, the skill MUST explicitly stop, inform the user, and only continue after the user opts in (or the caller passes `--no-review` / sets `require_vision_llm=false` in `scripts/config.json`) — silent fallback to structural-only is removed.
- `SKILL.md` edge-case matrix updated: "Vision LLM unavailable / rate-limited" now stops for user consent before degrading to `review_mode = "structural-only"`.
- `assets/templates/visual-review-prompt.md` gains a top-of-file "Mandatory reviewer type" banner, explicit `attach as image input` guidance for `_review.png`, and a rewritten Fallback section that spells out the opt-in preconditions.

### Added
- `scripts/config.json`: new `require_vision_llm: true` flag to enforce the vision-LLM default at the configuration layer.

## [0.3.0] - 2026-07-14
### Changed
- **Repository layout now conforms to the [SkillHub publish spec](https://skillhub.cn/tutorials#publish-manage-skill).**
  - `skill/SKILL.md` → `SKILL.md` at the project root (SkillHub's required entry point).
  - `templates/` → `assets/templates/` (SkillHub treats `assets/` as the canonical home for templates and resource files).
- `SKILL.md` frontmatter gains a `tags: [design, svg, logo, brand, vector, icon]` array as recommended by the SkillHub sample.
- `scripts/deploy_skill.py` copies from the new locations (`SKILL.md`, `references/`, `assets/`, `scripts/`).
- `scripts/release.py` — `INCLUDE_PATHS`, `SKILL_FILE` constant, managed-file set, and commit staging all updated to the new layout.
- English & Chinese READMEs: repository-layout tree, "publishing" section, and every link into `templates/*` retargeted at `assets/templates/*`; former "clawhub" references replaced with SkillHub.

### Fixed
- `scripts/release.py` push stage now checks `git diff --cached --name-only` after staging and only invokes `git commit` when there really are staged changes — previously it unconditionally committed, so a preflight with no version-number diff would fail with `git commit` exit code 1.

### Migration
- If you had a local checkout on `0.2.0`, re-run `python scripts/deploy_skill.py` after pulling — the old `skill/` and `templates/` directories are gone and any external references to them (e.g. custom scripts) must be pointed at `SKILL.md` / `assets/templates/*` respectively.

## [0.2.0] - 2026-07-14
### Added
- `scripts/config.json`: multi-mirror CDN list (`cdn_url_templates`) with jsDelivr / fastly / gcore / `jsd.onmicrosoft.cn` / unpkg / raw.githubusercontent fallbacks, plus `fetch_retries_per_url` and `fetch_timeout_seconds` tuning knobs.
- `scripts/fetch_samples.py`: mirror iteration with exponential backoff, SVG payload sanity check, per-slug failure reporting, and non-zero exit code when all mirrors fail.
- `scripts/validate_svg.py`: bilingual (English + 中文) structured violations via a `Violation` dataclass, actionable `fix` suggestions, safe XML `parse-error` handling, and a new `--json` output mode for CI/tooling.
- `skill/SKILL.md`: `--max-iterations` override, iteration history + `_review-summary.md`, a `review_mode = "structural-only"` graceful-degradation path, an edge-case matrix, an FAQ + anti-patterns section, and a full NovaSync end-to-end walk-through.
- `templates/visual-review-prompt.md`: explicit "no vision LLM" fallback contract with an `accept-structural-only` JSON template that forbids fabricated scores.

### Changed
- Legacy `cdn_url_template` (singular) is still honoured as the first mirror candidate — no breaking changes for existing configs.
- `validate_svg.py` human-readable output is now multi-line per violation (code / EN / 中文 / fix); programmatic consumers should switch to `--json`.

## [0.1.0] - 2026-07-14
### Added
- Initial public release of the `logo-svg-generator` TRAE skill.
- Simple-Icons-compliant SVG generation pipeline with iterative vision-LLM review.
- References: `design-rules.md`, `motif-patterns.md`, `sample-icons.md`.
- Templates: `visual-review-prompt.md`, `concept-brief-template.md`.
- Scripts: `fetch_samples.py`, `validate_svg.py`, `render_previews.py`,
  `export_variants.py`, `simplify_for_small.py`, `deploy_skill.py`.
- Three ready-to-run examples: NovaSync, LumenDB, PulseMail.
- English + Chinese README, MIT license.
- Release helper script `scripts/release.py`.
