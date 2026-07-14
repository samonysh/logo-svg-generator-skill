# Changelog

All notable changes to **logo-svg-generator** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
