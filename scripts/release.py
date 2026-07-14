#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""发布脚本 · Release helper for logo-svg-generator.

一条命令完成三件事：
1. Preflight: 检查发版前置条件（干净的 git 工作区、gh 已登录、CHANGELOG 有当前版本记录），
   并把 VERSION、CHANGELOG、skill/SKILL.md 等文件中的版本号统一。
2. Push:     提交版本号变更、打 tag、推送到 GitHub。
3. Release:  打包 release zip，创建 GitHub Release 并上传附件。

用法示例：
    python scripts/release.py preflight --version 0.2.0
    python scripts/release.py push      --version 0.2.0
    python scripts/release.py release   --version 0.2.0
    python scripts/release.py all       --version 0.2.0        # 一次跑完三步

依赖：
    * git         必须在 PATH 中
    * gh          GitHub CLI，必须已 `gh auth login`
    * python 3.10+
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

# ---------------------------------------------------------------------------
# 常量与路径
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
VERSION_FILE = ROOT / "VERSION"
CHANGELOG_FILE = ROOT / "CHANGELOG.md"
SKILL_FILE = ROOT / "skill" / "SKILL.md"
DIST_DIR = ROOT / "dist"

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")

# 打包时需要包含 / 排除的路径（相对 ROOT）
INCLUDE_PATHS = [
    "skill",
    "references",
    "templates",
    "scripts",
    "examples",
    "README.md",
    "README.zh-CN.md",
    "LICENSE",
    "CHANGELOG.md",
    "VERSION",
    ".gitignore",
]
EXCLUDE_DIR_NAMES = {"__pycache__", ".venv", "venv", "env", ".pytest_cache",
                      ".mypy_cache", ".idea", ".vscode", "samples", "output",
                      "dist", ".git"}
EXCLUDE_FILE_SUFFIXES = {".pyc", ".pyo", ".pyd", ".swp"}


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------


class ReleaseError(RuntimeError):
    """发版流程中的可预期错误。"""


def _c(text: str, color: str) -> str:
    codes = {"red": "31", "green": "32", "yellow": "33", "blue": "34",
             "magenta": "35", "cyan": "36", "bold": "1"}
    if not sys.stdout.isatty():
        return text
    return f"\033[{codes[color]}m{text}\033[0m"


def info(msg: str) -> None:
    print(f"{_c('[INFO]', 'cyan')} {msg}")


def ok(msg: str) -> None:
    print(f"{_c('[ OK ]', 'green')} {msg}")


def warn(msg: str) -> None:
    print(f"{_c('[WARN]', 'yellow')} {msg}")


def fail(msg: str) -> "None":
    raise ReleaseError(msg)


def run(cmd: list[str], *, check: bool = True, capture: bool = False,
        cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    """封装 subprocess.run，默认 UTF-8 文本输出。"""
    display = " ".join(cmd)
    info(f"$ {display}")
    result = subprocess.run(
        cmd,
        cwd=str(cwd or ROOT),
        check=False,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )
    if check and result.returncode != 0:
        stderr = (result.stderr or "").strip()
        stdout = (result.stdout or "").strip()
        detail = stderr or stdout or f"exit code = {result.returncode}"
        fail(f"命令失败: {display}\n{detail}")
    return result


def which_or_fail(binary: str) -> None:
    if shutil.which(binary) is None:
        fail(f"未在 PATH 中找到可执行文件: {binary}")


def read_version() -> str:
    if not VERSION_FILE.exists():
        fail(f"缺少 VERSION 文件: {VERSION_FILE}")
    v = VERSION_FILE.read_text(encoding="utf-8").strip()
    if not SEMVER_RE.match(v):
        fail(f"VERSION 文件中的版本号不合法: {v!r}（应形如 1.2.3）")
    return v


def validate_semver(v: str) -> str:
    if not SEMVER_RE.match(v):
        fail(f"版本号不合法: {v!r}（应形如 1.2.3 / 1.2.3-rc.1）")
    return v


# ---------------------------------------------------------------------------
# Stage 1: preflight —— 检查发版条件 & 统一版本号
# ---------------------------------------------------------------------------


def stage_preflight(version: str, *, allow_dirty: bool = False) -> None:
    info(f"=== Stage 1 / Preflight · v{version} ===")

    # 1. 二进制依赖
    which_or_fail("git")
    which_or_fail("gh")

    # 2. gh 已登录
    r = run(["gh", "auth", "status"], check=False, capture=True)
    if r.returncode != 0:
        fail("GitHub CLI 未登录，请先运行 `gh auth login`。")
    ok("GitHub CLI 已登录")

    # 3. git 仓库
    if not (ROOT / ".git").exists():
        fail("当前目录不是 git 仓库，请先执行 `git init` 并配置 remote。")

    # 4. remote 已配置
    r = run(["git", "remote", "get-url", "origin"], check=False, capture=True)
    if r.returncode != 0:
        fail("git remote `origin` 未配置，请先 `git remote add origin ...`。")
    ok(f"remote origin = {r.stdout.strip()}")

    # 5. 工作区状态
    r = run(["git", "status", "--porcelain"], capture=True)
    if r.stdout.strip():
        # preflight 阶段会修改版本号，允许存在这些未提交的改动
        # 但如果用户有其它未提交内容，需要 --allow-dirty
        dirty_files = [line[3:] for line in r.stdout.splitlines()]
        managed = {"VERSION", "CHANGELOG.md", "skill/SKILL.md"}
        other = [f for f in dirty_files if f not in managed]
        if other and not allow_dirty:
            fail("工作区存在未提交的变更（非版本号相关）：\n  "
                 + "\n  ".join(other)
                 + "\n请先提交或加 --allow-dirty。")

    # 6. tag 冲突
    tag = f"v{version}"
    r = run(["git", "tag", "--list", tag], capture=True)
    if r.stdout.strip():
        fail(f"tag {tag} 已存在，请先删除或使用新版本号。")
    ok(f"tag {tag} 可用")

    # 7. 统一版本号
    _write_version_file(version)
    _stamp_changelog(version)
    _stamp_skill_frontmatter(version)

    ok(f"Preflight 通过，版本号已统一为 {version}")


def _write_version_file(version: str) -> None:
    VERSION_FILE.write_text(version + "\n", encoding="utf-8")
    ok(f"写入 {VERSION_FILE.relative_to(ROOT)}")


def _stamp_changelog(version: str) -> None:
    """确保 CHANGELOG 存在当前版本的段落。若只有 [Unreleased]，替换为 [version] - date。"""
    if not CHANGELOG_FILE.exists():
        warn(f"未找到 {CHANGELOG_FILE.name}，跳过 stamp。")
        return
    text = CHANGELOG_FILE.read_text(encoding="utf-8")
    header_pat = re.compile(rf"^## \[{re.escape(version)}\]", re.M)
    if header_pat.search(text):
        ok(f"CHANGELOG 已包含 [{version}] 段落")
        return

    from datetime import date
    today = date.today().isoformat()
    if re.search(r"^## \[Unreleased\]\s*$", text, re.M):
        text = re.sub(
            r"^## \[Unreleased\]\s*$",
            f"## [Unreleased]\n\n## [{version}] - {today}",
            text,
            count=1,
            flags=re.M,
        )
        CHANGELOG_FILE.write_text(text, encoding="utf-8")
        ok(f"CHANGELOG 已追加 [{version}] - {today}")
    else:
        warn(f"CHANGELOG 中找不到 [Unreleased] 或 [{version}]，请手动更新。")


def _stamp_skill_frontmatter(version: str) -> None:
    """把版本号写入 skill/SKILL.md 的 frontmatter（若还没有 version 字段则追加）。"""
    if not SKILL_FILE.exists():
        warn(f"未找到 {SKILL_FILE.relative_to(ROOT)}，跳过。")
        return
    text = SKILL_FILE.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        warn("skill/SKILL.md 无 frontmatter 段，跳过版本注入。")
        return
    fm = m.group(1)
    if re.search(r"^version:\s*", fm, re.M):
        new_fm = re.sub(r"^version:\s*.*$", f'version: "{version}"', fm, flags=re.M)
    else:
        new_fm = fm.rstrip() + f'\nversion: "{version}"'
    new_text = text.replace(m.group(0), f"---\n{new_fm}\n---\n", 1)
    SKILL_FILE.write_text(new_text, encoding="utf-8")
    ok(f"skill/SKILL.md frontmatter 版本号 -> {version}")


# ---------------------------------------------------------------------------
# Stage 2: push —— 提交、打 tag、推送
# ---------------------------------------------------------------------------


def stage_push(version: str, *, remote: str = "origin",
               branch: str | None = None) -> None:
    info(f"=== Stage 2 / Push · v{version} ===")

    tag = f"v{version}"

    # 当前分支
    r = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture=True)
    current_branch = r.stdout.strip()
    branch = branch or current_branch
    info(f"当前分支: {current_branch}，推送到 {remote}/{branch}")

    # 若有版本号相关的变更，提交它
    r = run(["git", "status", "--porcelain"], capture=True)
    if r.stdout.strip():
        run(["git", "add", "VERSION", "CHANGELOG.md", "skill/SKILL.md"], check=False)
        # 兜底：把剩余的都加上
        run(["git", "add", "-A"])
        run(["git", "commit", "-m", f"chore(release): v{version}"])
        ok(f"已提交 chore(release): v{version}")
    else:
        info("无需新增 commit")

    # 打 tag
    run(["git", "tag", "-a", tag, "-m", f"Release {tag}"])
    ok(f"已打 tag {tag}")

    # 推送
    run(["git", "push", remote, branch])
    run(["git", "push", remote, tag])
    ok(f"已推送分支与 tag 到 {remote}")


# ---------------------------------------------------------------------------
# Stage 3: release —— 打包 zip，创建 GitHub Release
# ---------------------------------------------------------------------------


def stage_release(version: str, *, draft: bool = False,
                  prerelease: bool = False,
                  notes_file: Path | None = None) -> None:
    info(f"=== Stage 3 / Release · v{version} ===")

    tag = f"v{version}"
    DIST_DIR.mkdir(exist_ok=True)
    zip_path = DIST_DIR / f"logo-svg-generator-{version}.zip"
    _build_zip(zip_path)

    notes = _extract_release_notes(version) if notes_file is None else notes_file.read_text(encoding="utf-8")

    # 若已存在 release，则改为 upload；否则 create
    r = run(["gh", "release", "view", tag], check=False, capture=True)
    if r.returncode == 0:
        info(f"GitHub Release {tag} 已存在，追加上传附件 …")
        run(["gh", "release", "upload", tag, str(zip_path), "--clobber"])
    else:
        cmd = ["gh", "release", "create", tag,
               str(zip_path),
               "--title", f"logo-svg-generator {tag}",
               "--notes", notes]
        if draft:
            cmd.append("--draft")
        if prerelease:
            cmd.append("--prerelease")
        run(cmd)

    ok(f"Release {tag} 完成，附件: {zip_path.relative_to(ROOT)}")


def _build_zip(zip_path: Path) -> None:
    if zip_path.exists():
        zip_path.unlink()
    info(f"打包 -> {zip_path.relative_to(ROOT)}")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel in INCLUDE_PATHS:
            src = ROOT / rel
            if not src.exists():
                warn(f"跳过不存在的路径: {rel}")
                continue
            if src.is_file():
                zf.write(src, arcname=rel)
            else:
                _add_dir_to_zip(zf, src)
    ok(f"打包完成 ({zip_path.stat().st_size / 1024:.1f} KB)")


def _add_dir_to_zip(zf: zipfile.ZipFile, base: Path) -> None:
    for p in base.rglob("*"):
        if any(part in EXCLUDE_DIR_NAMES for part in p.parts):
            continue
        if p.suffix in EXCLUDE_FILE_SUFFIXES:
            continue
        if p.is_file():
            zf.write(p, arcname=str(p.relative_to(ROOT)).replace(os.sep, "/"))


def _extract_release_notes(version: str) -> str:
    """从 CHANGELOG 抽取该版本的段落作为 release notes。"""
    fallback = f"Release {version}."
    if not CHANGELOG_FILE.exists():
        return fallback
    text = CHANGELOG_FILE.read_text(encoding="utf-8")
    pat = re.compile(
        rf"^## \[{re.escape(version)}\].*?(?=^## \[|\Z)",
        re.M | re.S,
    )
    m = pat.search(text)
    if not m:
        warn(f"CHANGELOG 中找不到 [{version}] 段落，使用默认 release notes。")
        return fallback
    return m.group(0).strip()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--version", required=False,
                        help="目标版本号（形如 0.2.0）。省略时从 VERSION 文件读取。")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="release.py",
        description="logo-svg-generator 发版脚本",
    )
    sub = parser.add_subparsers(dest="stage", required=True)

    p_pre = sub.add_parser("preflight", help="检查发版条件并统一版本号")
    _add_common(p_pre)
    p_pre.add_argument("--allow-dirty", action="store_true",
                       help="允许工作区存在非版本号文件的未提交变更")

    p_push = sub.add_parser("push", help="提交、打 tag、推送到 GitHub")
    _add_common(p_push)
    p_push.add_argument("--remote", default="origin")
    p_push.add_argument("--branch", default=None,
                        help="推送到的分支名，默认使用当前分支")

    p_rel = sub.add_parser("release", help="打包 zip 并创建 GitHub Release")
    _add_common(p_rel)
    p_rel.add_argument("--draft", action="store_true", help="创建为草稿")
    p_rel.add_argument("--prerelease", action="store_true", help="标记为预发布")
    p_rel.add_argument("--notes-file", type=Path, default=None,
                       help="使用外部文件作为 release notes，覆盖 CHANGELOG 抽取")

    p_all = sub.add_parser("all", help="preflight + push + release 一次跑完")
    _add_common(p_all)
    p_all.add_argument("--allow-dirty", action="store_true")
    p_all.add_argument("--remote", default="origin")
    p_all.add_argument("--branch", default=None)
    p_all.add_argument("--draft", action="store_true")
    p_all.add_argument("--prerelease", action="store_true")
    p_all.add_argument("--notes-file", type=Path, default=None)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    version = validate_semver(args.version) if args.version else read_version()

    try:
        if args.stage == "preflight":
            stage_preflight(version, allow_dirty=args.allow_dirty)
        elif args.stage == "push":
            stage_push(version, remote=args.remote, branch=args.branch)
        elif args.stage == "release":
            stage_release(version, draft=args.draft,
                          prerelease=args.prerelease,
                          notes_file=args.notes_file)
        elif args.stage == "all":
            stage_preflight(version, allow_dirty=args.allow_dirty)
            stage_push(version, remote=args.remote, branch=args.branch)
            stage_release(version, draft=args.draft,
                          prerelease=args.prerelease,
                          notes_file=args.notes_file)
        else:  # pragma: no cover
            parser.error(f"未知阶段: {args.stage}")
    except ReleaseError as exc:
        print(f"{_c('[FAIL]', 'red')} {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print(f"\n{_c('[ABRT]', 'yellow')} 已中断", file=sys.stderr)
        return 130

    print(_c("Done.", "green"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
