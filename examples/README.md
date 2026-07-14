# Examples

This folder contains ready-to-run product briefs for the `logo-svg-generator` skill. Each example folder holds:

- `brief.md` — natural-language brief; copy-paste it into TRAE, or ask TRAE to run the skill on this file.
- `README.md` — expected motifs, palette, and success criteria.

## How to run

After you have deployed the skill (`python scripts\deploy_skill.py`), open TRAE and say:

> Please use the `logo-svg-generator` skill on `examples/01-novasync/brief.md`.

TRAE will read the brief, generate a 24×24 master, run the vision-review loop, and drop the deliverables under `output/<slug>/`.

## Examples

| # | Slug | Domain | Motif hint | Brand hex |
|---|---|---|---|---|
| 1 | `novasync` | File sync | Letter N + orbit arrows | `#4F46E5` (indigo) |
| 2 | `lumendb`  | Analytics DB | Prism + data spark | `#0EA5A5` (teal) |
| 3 | `pulsemail` | Email client | Envelope + pulse waveform | `#EF4444` (coral) |
