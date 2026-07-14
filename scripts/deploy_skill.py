"""deploy_skill.py — copy skill/ + references/ + templates/ into .trae/skills/logo-svg-generator/.

Run from the project root:
    python scripts/deploy_skill.py                 # deploy to d:\CODE\.trae\skills
    python scripts/deploy_skill.py --target C:\\path\\to\\.trae\\skills
"""
from __future__ import annotations
import argparse
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DEFAULT_TARGET = Path(r"d:\CODE\.trae\skills")


def deploy(target_root: Path) -> None:
    dest = target_root / "logo-svg-generator"
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)

    # 1) SKILL.md at the root of the skill folder
    shutil.copy(ROOT / "skill" / "SKILL.md", dest / "SKILL.md")

    # 2) supporting content copied in-place; SKILL.md's `../references/...` links
    #    resolve because SKILL.md sits at dest/ and we place references at dest/references/
    for name in ("references", "templates", "scripts"):
        src = ROOT / name
        if src.exists():
            shutil.copytree(src, dest / name)

    (dest / "README.md").write_text(
        "# logo-svg-generator (deployed)\n\n"
        "This is a deployed copy. The authoring project lives at "
        f"`{ROOT}`.\n",
        encoding="utf-8",
    )
    print(f"[deployed] {dest}")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    args = ap.parse_args(argv[1:])
    args.target.mkdir(parents=True, exist_ok=True)
    deploy(args.target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
