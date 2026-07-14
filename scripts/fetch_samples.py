"""fetch_samples.py — download reference SVGs from the simple-icons CDN.

Usage:
    python fetch_samples.py                # uses scripts/config.json's default list
    python fetch_samples.py github apple    # override with explicit slugs
"""
from __future__ import annotations
import json
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CFG = json.loads((HERE / "config.json").read_text(encoding="utf-8"))


def fetch(slug: str, out_dir: Path) -> Path:
    url = CFG["cdn_url_template"].format(slug=slug)
    out = out_dir / f"{slug}.svg"
    print(f"[fetch] {slug} <- {url}")
    with urllib.request.urlopen(url, timeout=30) as r:
        data = r.read()
    out.write_bytes(data)
    return out


def main(argv: list[str]) -> int:
    slugs = argv[1:] if len(argv) > 1 else CFG["sample_slugs_to_fetch"]
    out_dir = ROOT / CFG["samples_root"]
    out_dir.mkdir(parents=True, exist_ok=True)
    ok = 0
    for slug in slugs:
        try:
            fetch(slug, out_dir)
            ok += 1
        except Exception as e:
            print(f"[warn] failed {slug}: {e}", file=sys.stderr)
    print(f"[done] {ok}/{len(slugs)} icons saved to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
