# Changelog

All notable changes to **logo-svg-generator** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
