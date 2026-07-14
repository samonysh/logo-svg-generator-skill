"""validate_svg.py — enforce Simple-Icons compliance on a generated master SVG.

Usage:
    python validate_svg.py path/to/master-24.svg
    python validate_svg.py path/to/master-24.svg --json     # machine-readable output

Exit code 0 if compliant; 1 otherwise. Prints violations to stderr.

Every violation includes:
    * a stable `code` for programmatic handling,
    * an English one-liner explaining what went wrong,
    * a Chinese translation, and
    * a `fix` sentence suggesting the smallest edit that unblocks compliance.

Downstream callers (the SKILL loop, the deploy step, CI) should consume the
`--json` form so they can surface actionable messages to end users instead of
opaque tracebacks.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

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


@dataclass
class Violation:
    code: str
    message: str          # English, one line
    message_zh: str       # 中文简述
    fix: str              # concrete next step

    def format_line(self) -> str:
        return f"  - [{self.code}] {self.message}\n    · 中文: {self.message_zh}\n    · fix: {self.fix}"


def _err(bag: list[Violation], code: str, en: str, zh: str, fix: str) -> None:
    bag.append(Violation(code=code, message=en, message_zh=zh, fix=fix))


def validate(svg_path: Path) -> list[Violation]:
    text = svg_path.read_text(encoding="utf-8").strip()
    errs: list[Violation] = []

    if text.startswith("<?xml"):
        _err(errs, "no-xml-decl",
             "XML declaration (<?xml ...?>) is not allowed at the root.",
             "根节点前不允许出现 XML 声明。",
             "delete the leading `<?xml ...?>` line.")
    if "<!DOCTYPE" in text:
        _err(errs, "no-doctype",
             "DOCTYPE is not allowed.",
             "不允许出现 DOCTYPE。",
             "remove the <!DOCTYPE ...> line.")
    if "<!--" in text:
        _err(errs, "no-comments",
             "XML comments are not allowed.",
             "不允许出现 <!-- --> 注释。",
             "delete every <!-- ... --> block; move any explanation into commit messages.")

    try:
        root = ET.fromstring(text)
    except ET.ParseError as e:
        _err(errs, "parse-error",
             f"SVG is not well-formed XML: {e}",
             f"SVG 不是合法 XML：{e}",
             "check that every tag is closed and attribute values are quoted; run through an XML validator.")
        return errs

    if strip_ns(root.tag) != "svg":
        _err(errs, "root-tag",
             f"expected root <svg>, got <{strip_ns(root.tag)}>",
             f"根节点必须是 <svg>，实际是 <{strip_ns(root.tag)}>。",
             "wrap the content in <svg role=\"img\" viewBox=\"0 0 24 24\" xmlns=\"http://www.w3.org/2000/svg\">.")

    if root.get("role") != "img":
        _err(errs, "root-role",
             'root <svg> must have role="img".',
             "根 <svg> 必须带 role=\"img\"。",
             'add role="img" as the first attribute of <svg>.')
    if root.get("viewBox") != "0 0 24 24":
        _err(errs, "root-viewbox",
             f'viewBox must be "0 0 24 24"; got {root.get("viewBox")!r}.',
             f"viewBox 必须是 \"0 0 24 24\"，当前是 {root.get('viewBox')!r}。",
             "set viewBox=\"0 0 24 24\" and rescale coordinates uniformly to fit that canvas.")
    ns_ok = root.tag.startswith("{http://www.w3.org/2000/svg}") or (root.get("xmlns") or "").endswith("2000/svg")
    if not ns_ok:
        _err(errs, "root-xmlns",
             'xmlns must be "http://www.w3.org/2000/svg".',
             "xmlns 必须是 \"http://www.w3.org/2000/svg\"。",
             'add xmlns="http://www.w3.org/2000/svg" to the <svg> element.')

    titles = [c for c in root if strip_ns(c.tag) == "title"]
    if len(titles) != 1:
        _err(errs, "title-count",
             f"expected exactly 1 <title>, got {len(titles)}.",
             f"必须有且仅有 1 个 <title>，当前是 {len(titles)} 个。",
             "keep one <title>Brand Name</title> as the first child of <svg>.")
    elif not (titles[0].text and titles[0].text.strip()):
        _err(errs, "title-empty",
             "<title> is empty.",
             "<title> 内容为空。",
             "write the brand's canonical name inside the <title> tags.")

    paths = [c for c in root if strip_ns(c.tag) == "path"]
    if len(paths) != 1:
        _err(errs, "path-count",
             f"expected exactly 1 <path>, got {len(paths)}.",
             f"必须有且仅有 1 个 <path>，当前是 {len(paths)} 个。",
             "merge all shapes into one compound <path> using sub-paths (M ... Z M ... Z).")

    for c in root:
        t = strip_ns(c.tag)
        if t in FORBIDDEN_ELEMENTS:
            _err(errs, "element-forbidden",
                 f"<{t}> is forbidden; only <title> and <path> are allowed.",
                 f"禁止使用 <{t}>，只允许 <title> 与 <path>。",
                 f"convert the <{t}> into a <path> command (e.g., <circle> → M...A...Z) and delete the original tag.")
        elif t not in {"title", "path"}:
            _err(errs, "element-unexpected",
                 f"unexpected <{t}> as a child of <svg>.",
                 f"<svg> 下不应出现 <{t}>。",
                 f"remove the <{t}> element; only <title> and <path> are permitted.")

    if paths:
        p = paths[0]
        d = p.get("d") or ""
        for k in list(p.attrib):
            local = strip_ns(k)
            if local in FORBIDDEN_PATH_ATTRS:
                _err(errs, f"path-attr-{local}",
                     f"attribute '{local}' is forbidden on the master path.",
                     f"master <path> 不允许携带 '{local}' 属性。",
                     f"delete the {local}=... attribute; color is applied only to color/ variants.")
        if not d:
            _err(errs, "path-d-empty",
                 "<path> has no `d` attribute.",
                 "<path> 缺少 `d` 属性。",
                 "supply a path data string, e.g., d=\"M0 0h24v24H0z\".")
        else:
            # Structural check only. See SKILL.md Step 4 for geometric review.
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


def _print_human(path: Path, errs: list[Violation]) -> None:
    if not errs:
        print(f"[OK] {path}")
        return
    print(f"[FAIL] {path}", file=sys.stderr)
    for v in errs:
        print(v.format_line(), file=sys.stderr)


def _print_json(path: Path, errs: list[Violation]) -> None:
    payload: dict[str, Any] = {
        "file": str(path),
        "ok": not errs,
        "violations": [asdict(v) for v in errs],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="validate_svg.py")
    ap.add_argument("svg", type=Path)
    ap.add_argument("--json", action="store_true",
                    help="emit a machine-readable JSON report on stdout")
    args = ap.parse_args(argv[1:])
    errs = validate(args.svg)
    if args.json:
        _print_json(args.svg, errs)
    else:
        _print_human(args.svg, errs)
    return 0 if not errs else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
