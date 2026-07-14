"""render_previews.py — rasterize a master SVG into a review sheet PNG.

Usage:
    python render_previews.py path/to/master-24.svg [--out output/<slug>]

Layout of the review sheet (600×420 canvas, 2× DPI for clarity):
    Row 1: 32/64/128/256/512 on WHITE background
    Row 2: 32/64/128/256/512 on BLACK background
    Row 3: 256 in a rounded-square "app-icon" frame + 64-px grid overlay on 256

Requires: cairosvg + Pillow (both pure-Python-ish; cairosvg needs cairo).
If cairosvg is unavailable, falls back to resvg CLI or Inkscape if on PATH.
"""
from __future__ import annotations
import argparse
import io
import shutil
import subprocess
import sys
from pathlib import Path

SIZES = [32, 64, 128, 256, 512]


def rasterize(svg_path: Path, size: int) -> bytes:
    """Return PNG bytes for the SVG rendered at size×size."""
    try:
        import cairosvg  # type: ignore
        return cairosvg.svg2png(url=str(svg_path), output_width=size, output_height=size)
    except Exception:
        pass
    for tool in ("resvg", "inkscape"):
        if shutil.which(tool):
            out = svg_path.with_suffix(f".{size}.png")
            if tool == "resvg":
                subprocess.run([tool, "-w", str(size), "-h", str(size), str(svg_path), str(out)], check=True)
            else:  # inkscape
                subprocess.run([tool, "-w", str(size), "-h", str(size), "-o", str(out), str(svg_path)], check=True)
            return out.read_bytes()
    raise RuntimeError("No SVG rasterizer available (install cairosvg, resvg, or inkscape).")


def build_review_sheet(svg_path: Path, out_path: Path) -> Path:
    from PIL import Image, ImageDraw
    W, H = 1200, 900
    sheet = Image.new("RGB", (W, H), "#EEEEEE")
    draw = ImageDraw.Draw(sheet)

    # Row 1 (WHITE) and Row 2 (BLACK) — small tiles
    tile_w = W // len(SIZES)
    for row, (bg, fg_hint) in enumerate([("#FFFFFF", "black"), ("#111111", "white")]):
        y = row * 250 + 20
        for i, s in enumerate(SIZES):
            box = Image.new("RGB", (tile_w - 20, 220), bg)
            png = Image.open(io.BytesIO(rasterize(svg_path, s))).convert("RGBA")
            # invert master to visible on black by drawing on transparent - but master path already black;
            # for the black row, paint icon in white by using PIL fill:
            if row == 1:
                # simple invert: put a white shape via alpha
                alpha = png.split()[-1]
                white_layer = Image.new("RGBA", png.size, (255, 255, 255, 255))
                white_layer.putalpha(alpha)
                png = white_layer
            box.paste(png, ((tile_w - 20 - s) // 2, (220 - s) // 2), png)
            sheet.paste(box, (i * tile_w + 10, y))
            draw.text((i * tile_w + 12, y + 222), f"{s}px", fill="#333")

    # Row 3 — app-icon frame + grid overlay
    y = 520
    app = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    mask = Image.new("L", (256, 256), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, 255, 255], radius=56, fill=255)
    frame = Image.new("RGB", (256, 256), "#4F46E5")
    frame.putalpha(mask)
    png = Image.open(io.BytesIO(rasterize(svg_path, 200))).convert("RGBA")
    alpha = png.split()[-1]
    white_icon = Image.new("RGBA", png.size, (255, 255, 255, 255))
    white_icon.putalpha(alpha)
    app.paste(frame, (0, 0), frame)
    app.paste(white_icon, ((256 - 200) // 2, (256 - 200) // 2), white_icon)
    sheet.paste(app, (40, y), app)
    draw.text((40, y + 260), "App-icon (256, indigo rounded square)", fill="#333")

    # 64-px grid overlay on a 512 render
    big = Image.open(io.BytesIO(rasterize(svg_path, 512))).convert("RGBA")
    canvas = Image.new("RGB", (512, 512), "#FFFFFF")
    canvas.paste(big, (0, 0), big)
    dd = ImageDraw.Draw(canvas)
    for i in range(0, 513, 512 // 24):  # 24 grid lines matching 24-unit viewBox
        dd.line([(i, 0), (i, 512)], fill=(220, 220, 220), width=1)
        dd.line([(0, i), (512, i)], fill=(220, 220, 220), width=1)
    dd.line([(256, 0), (256, 512)], fill=(255, 100, 100), width=1)
    dd.line([(0, 256), (512, 256)], fill=(255, 100, 100), width=1)
    sheet.paste(canvas.resize((320, 320)), (400, y))
    draw.text((400, y + 322), "24×24 grid overlay (center in red)", fill="#333")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path, "PNG")
    print(f"[review] wrote {out_path}")
    return out_path


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("svg", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args(argv[1:])
    out = args.out or args.svg.parent / "_review.png"
    build_review_sheet(args.svg, out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
