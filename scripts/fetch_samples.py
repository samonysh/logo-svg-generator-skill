"""fetch_samples.py — download reference SVGs from the simple-icons CDN.

Usage:
    python fetch_samples.py                # uses scripts/config.json's default list
    python fetch_samples.py github apple    # override with explicit slugs

Robustness:
    * Reads CDN mirrors from `config.json.cdn_url_templates` in order and falls
      back to the next mirror on any HTTP/network failure. This matters
      especially for mainland-China users where `cdn.jsdelivr.net` can be
      intermittently blocked — the list includes fastly / gcore / unpkg /
      raw.githubusercontent as progressively more resilient fallbacks.
    * Retries each URL up to `fetch_retries_per_url` times with a short
      exponential backoff.
    * The legacy `config.json.cdn_url_template` (singular) is honoured as the
      first candidate for backwards compatibility.
"""
from __future__ import annotations
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CFG = json.loads((HERE / "config.json").read_text(encoding="utf-8"))


def _cdn_templates() -> list[str]:
    urls: list[str] = []
    legacy = CFG.get("cdn_url_template")
    if isinstance(legacy, str) and legacy:
        urls.append(legacy)
    for u in CFG.get("cdn_url_templates", []) or []:
        if isinstance(u, str) and u and u not in urls:
            urls.append(u)
    if not urls:
        raise RuntimeError(
            "No CDN URL configured. Set `cdn_url_templates` in scripts/config.json."
        )
    return urls


def fetch(slug: str, out_dir: Path) -> Path:
    templates = _cdn_templates()
    retries = int(CFG.get("fetch_retries_per_url", 2))
    timeout = int(CFG.get("fetch_timeout_seconds", 15))

    last_err: Exception | None = None
    for tpl in templates:
        url = tpl.format(slug=slug)
        for attempt in range(1, retries + 1):
            try:
                print(f"[fetch] {slug} <- {url}  (attempt {attempt}/{retries})")
                req = urllib.request.Request(
                    url,
                    headers={"User-Agent": "logo-svg-generator/fetch-samples"},
                )
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    data = r.read()
                if not data or b"<svg" not in data[:200]:
                    raise RuntimeError("response does not look like an SVG")
                out = out_dir / f"{slug}.svg"
                out.write_bytes(data)
                return out
            except (urllib.error.URLError, TimeoutError, RuntimeError) as e:
                last_err = e
                print(f"  [retry] {e}", file=sys.stderr)
                time.sleep(min(2 ** (attempt - 1), 4))
        # move on to next mirror
    raise RuntimeError(f"all mirrors failed for slug={slug}: {last_err}")


def main(argv: list[str]) -> int:
    slugs = argv[1:] if len(argv) > 1 else CFG["sample_slugs_to_fetch"]
    out_dir = ROOT / CFG["samples_root"]
    out_dir.mkdir(parents=True, exist_ok=True)
    ok = 0
    failures: list[str] = []
    for slug in slugs:
        try:
            fetch(slug, out_dir)
            ok += 1
        except Exception as e:
            failures.append(slug)
            print(f"[warn] failed {slug}: {e}", file=sys.stderr)
    print(f"[done] {ok}/{len(slugs)} icons saved to {out_dir}")
    if failures:
        print(
            "[hint] some icons could not be fetched. This is usually a network / firewall\n"
            "       issue; the skill can still design from references/motif-patterns.md alone.\n"
            f"       Failed slugs: {', '.join(failures)}",
            file=sys.stderr,
        )
        return 1 if ok == 0 else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
