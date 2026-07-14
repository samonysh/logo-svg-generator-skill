# Example 03 — PulseMail

A pictogram with a horizontal "beat" element. Good stress-test for:

- **Two-motif composition** — envelope silhouette + pulse waveform, but must stay a single path.
- **Legibility at 16 px** — the waveform will be simplified via `scripts/simplify_for_small.py` for 16 / 24 px.
- **Warm palette** — coral fill should feel alive, not aggressive.

## Concept brief (auto-derived)

```yaml
product_name: "PulseMail"
slug: "pulsemail"
purpose: "focus-friendly email client with 3 daily pulses"
audience: ["knowledge_worker", "remote_team"]
mood_keywords: ["warm", "calm", "alive", "human"]
avoid_keywords: ["corporate", "cold", "sterile"]
preferred_color: "#EF4444"
metaphor_hints: "envelope + pulse waveform"
composition: "symbol_only"
shape_family: "pictogram"
```

## Expected deliverables

```
output/pulsemail/
├─ master-24.svg
├─ mono/…    color/…    png/…
├─ favicon/favicon.ico + apple-touch-icon-180.png
├─ brand.json
└─ _review.png
```

## Success criteria

- Envelope reads clearly at 16 px even after waveform simplification
- Vision-LLM `score ≥ 8.5` on the final iteration
- Passes `python scripts/validate_svg.py output/pulsemail/master-24.svg`
