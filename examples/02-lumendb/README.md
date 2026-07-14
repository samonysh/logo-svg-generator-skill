# Example 02 — LumenDB

A precise, data-flavored abstract mark. Good stress-test for:

- **Geometric shape family** — angular prism silhouette, not a letterform.
- **Ink balance** — the "spark" element is thin; the prism must carry weight without dominating.
- **Brand-fit at color** — teal fills must not muddy the negative-space triangle inside the prism.

## Concept brief (auto-derived)

```yaml
product_name: "LumenDB"
slug: "lumendb"
purpose: "realtime analytics database"
audience: ["data_engineer", "backend"]
mood_keywords: ["precise", "luminous", "fast", "engineered"]
avoid_keywords: ["biotech", "medical", "food"]
preferred_color: "#0EA5A5"
metaphor_hints: "prism refracting into a data spark"
composition: "symbol_only"
shape_family: "geometric"
```

## Expected deliverables

```
output/lumendb/
├─ master-24.svg
├─ mono/…    color/…    png/…
├─ favicon/favicon.ico + apple-touch-icon-180.png
├─ brand.json
└─ _review.png
```

## Success criteria

- Vision-LLM `score ≥ 8.5`
- Prism silhouette recognisable at 16 px
- Passes `python scripts/validate_svg.py output/lumendb/master-24.svg`
