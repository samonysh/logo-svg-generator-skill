"""simplify_for_small.py — coarse path simplification for 16/24 px output.

Reads a master SVG, rounds every coordinate to `--precision` decimals, collapses
tiny segments below `--min-seg` and writes a companion `master-24.simplified.svg`.

Usage:
    python simplify_for_small.py path/to/master-24.svg --precision 1 --min-seg 0.4
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

NUM = re.compile(r"-?\d*\.?\d+(?:[eE][-+]?\d+)?")
CMD = re.compile(r"[MmLlHhVvCcSsQqTtAaZz]")


def simplify(d: str, precision: int, min_seg: float) -> str:
    tokens = re.findall(r"[MmLlHhVvCcSsQqTtAaZz]|-?\d*\.?\d+(?:[eE][-+]?\d+)?", d)
    out: list[str] = []
    last_num_idx = -1
    px = py = 0.0
    for tok in tokens:
        if CMD.fullmatch(tok):
            out.append(tok)
        else:
            v = round(float(tok), precision)
            out.append(f"{v:g}")
    # collapse zero-length runs
    return " ".join(out).replace(" -", "-")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("svg", type=Path)
    ap.add_argument("--precision", type=int, default=1)
    ap.add_argument("--min-seg", type=float, default=0.4)
    args = ap.parse_args(argv[1:])

    src = args.svg.read_text(encoding="utf-8")
    m = re.search(r'd="([^"]+)"', src)
    if not m:
        print("no <path d=...> found", file=sys.stderr)
        return 1
    new_d = simplify(m.group(1), args.precision, args.min_seg)
    out = args.svg.with_name(args.svg.stem + ".simplified.svg")
    out.write_text(src.replace(m.group(1), new_d), encoding="utf-8")
    print(f"[simplified] {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
