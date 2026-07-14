"""export_variants.py — from an accepted master-24.svg, emit multi-size + color + PNG variants.

Usage:
    python export_variants.py path/to/master-24.svg --hex "#4F46E5" --slug novasync --title "NovaSync"
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CFG = json.loads((HERE / "config.json").read_text(encoding="utf-8"))

MASTER_RE = re.compile(
    r'<svg[^>]*viewBox="0 0 24 24"[^>]*>\s*<title>([^<]+)</title>\s*<path\s+d="([^"]+)"\s*/>\s*</svg>',
    re.DOTALL,
)


def parse_master(svg_text: str) -> tuple[str, str]:
    m = MASTER_RE.search(svg_text)
    if not m:
        raise ValueError("master SVG does not match the canonical shape")
    return m.group(1), m.group(2)


def build_svg(title: str, d: str, size: int, hex_color: str | None) -> str:
    fill = f' fill="{hex_color}"' if hex_color else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" role="img" '
        f'viewBox="0 0 24 24" width="{size}" height="{size}">'
        f'<title>{title}</title><path d="{d}"{fill}/></svg>'
    )


def maybe_rasterize(svg_text: str, out_png: Path, size: int) -> None:
    try:
        import cairosvg  # type: ignore
        cairosvg.svg2png(bytestring=svg_text.encode(), write_to=str(out_png),
                         output_width=size, output_height=size)
        print(f"  png -> {out_png}")
    except Exception as e:
        print(f"  [skip png {size}] {e}", file=sys.stderr)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("svg", type=Path)
    ap.add_argument("--hex", default=None)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args(argv[1:])

    src = args.svg.read_text(encoding="utf-8")
    _, d = parse_master(src)

    root = args.out or (Path(CFG["output_root"]) / args.slug)
    (root / "mono").mkdir(parents=True, exist_ok=True)
    (root / "color").mkdir(parents=True, exist_ok=True)
    (root / "png").mkdir(parents=True, exist_ok=True)

    # canonical master (unchanged)
    (root / "master-24.svg").write_text(src, encoding="utf-8")

    sizes = CFG["sizes"]
    for size in sizes:
        (root / "mono" / f"logo-{size}.svg").write_text(
            build_svg(args.title, d, size, None), encoding="utf-8")
        if args.hex:
            (root / "color" / f"logo-{size}.svg").write_text(
                build_svg(args.title, d, size, args.hex), encoding="utf-8")
        maybe_rasterize(build_svg(args.title, d, size, args.hex or "#000000"),
                        root / "png" / f"logo-{size}.png", size)

    (root / "brand.json").write_text(json.dumps({
        "slug": args.slug, "title": args.title, "hex": args.hex,
        "sizes": sizes, "generated_by": "logo-svg-generator skill",
    }, indent=2), encoding="utf-8")

    print(f"[done] variants written to {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
