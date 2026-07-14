"""validate_svg.py — enforce Simple-Icons compliance on a generated master SVG.

Usage:
    python validate_svg.py path/to/master-24.svg

Exit code 0 if compliant; 1 otherwise. Prints violations to stderr.
"""
from __future__ import annotations
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

NS = {"svg": "http://www.w3.org/2000/svg"}
ALLOWED_ROOT_ATTRS = {"role", "viewBox", "xmlns"}
FORBIDDEN_ELEMENTS = {
    "g", "rect", "circle", "ellipse", "polygon", "polyline", "line",
    "defs", "style", "use", "mask", "clipPath", "linearGradient", "radialGradient",
    "filter", "image", "text", "tspan",
}
FORBIDDEN_PATH_ATTRS = {"fill", "stroke", "class", "id", "style", "opacity"}


def strip_ns(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def validate(svg_path: Path) -> list[str]:
    text = svg_path.read_text(encoding="utf-8").strip()
    errs: list[str] = []

    if text.startswith("<?xml"):
        errs.append("root: XML declaration is not allowed")
    if "<!DOCTYPE" in text:
        errs.append("root: DOCTYPE is not allowed")
    if "<!--" in text:
        errs.append("root: XML comments are not allowed")

    root = ET.fromstring(text)
    if strip_ns(root.tag) != "svg":
        errs.append(f"root: expected <svg>, got <{strip_ns(root.tag)}>")

    if root.get("role") != "img":
        errs.append('root: role must be "img"')
    if root.get("viewBox") != "0 0 24 24":
        errs.append(f'root: viewBox must be "0 0 24 24", got {root.get("viewBox")!r}')
    # xmlns is folded into the tag namespace by ET; also accept raw attribute
    ns_ok = root.tag.startswith("{http://www.w3.org/2000/svg}") or (root.get("xmlns") or "").endswith("2000/svg")
    if not ns_ok:
        errs.append("root: xmlns must be http://www.w3.org/2000/svg")

    titles = [c for c in root if strip_ns(c.tag) == "title"]
    if len(titles) != 1:
        errs.append(f"title: expected exactly 1, got {len(titles)}")
    elif not (titles[0].text and titles[0].text.strip()):
        errs.append("title: must contain the brand name")

    paths = [c for c in root if strip_ns(c.tag) == "path"]
    if len(paths) != 1:
        errs.append(f"path: expected exactly 1, got {len(paths)}")

    for c in root:
        t = strip_ns(c.tag)
        if t in FORBIDDEN_ELEMENTS:
            errs.append(f"element: <{t}> is forbidden")
        elif t not in {"title", "path"}:
            errs.append(f"element: unexpected <{t}>")

    if paths:
        p = paths[0]
        d = p.get("d") or ""
        for k in list(p.attrib):
            if strip_ns(k) in FORBIDDEN_PATH_ATTRS:
                errs.append(f"path: attribute {strip_ns(k)!r} is forbidden on master")
        if not d:
            errs.append("path: d attribute is empty")
        else:
            # NOTE: exact bbox from a relative-heavy path needs a full path interpreter.
            # This validator only enforces STRUCTURAL rules. Geometric properties
            # (touches-two-sides, centering, ink coverage, readability) are covered by
            # the visual-review step (Step 4 of SKILL.md).
            pass

    return errs


_NUM_RE = re.compile(r"-?\d*\.?\d+(?:[eE][-+]?\d+)?")


def compute_bbox(d: str):
    """Crude bbox from all absolute-ish numbers in `d` (good enough for the compliance check)."""
    nums = [float(n) for n in _NUM_RE.findall(d)]
    if not nums:
        return None
    xs = nums[0::2]
    ys = nums[1::2]
    if not xs or not ys:
        return None
    return min(xs), min(ys), max(xs), max(ys)


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: validate_svg.py path/to/master.svg", file=sys.stderr)
        return 2
    errs = validate(Path(argv[1]))
    if errs:
        print(f"[FAIL] {argv[1]}", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print(f"[OK] {argv[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
