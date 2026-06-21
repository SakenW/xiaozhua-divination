#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

SKILL_NAME = "xiaozhua-divination"

ROOT_FILES = [
    "SKILL.md",
    "requirements.txt",
]

ROOT_DIRS = [
    "scripts",
    "liuyao",
    "qimen-dunjia",
    "ziwei-doushu",
    "bazi",
    "tarot",
    "astrology",
    "enneagram",
    "mbti",
]

FORBIDDEN_NAMES = {
    ".git",
    ".github",
    ".omx",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".DS_Store",
    "README.md",
    "LICENSE",
    ".gitignore",
    "dist",
    "tools",
    "tests",
    "dev",
    "releases",
}

FORBIDDEN_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".tmp",
    ".bak",
}


def ignored(_dir: str, names: list[str]) -> set[str]:
    out: set[str] = set()
    for name in names:
        path = Path(name)
        if name in FORBIDDEN_NAMES or path.suffix in FORBIDDEN_SUFFIXES:
            out.add(name)
    return out


def assert_clean_package(package_dir: Path) -> None:
    forbidden: list[str] = []
    for path in package_dir.rglob("*"):
        rel = path.relative_to(package_dir)
        parts = set(rel.parts)
        if parts & FORBIDDEN_NAMES or path.suffix in FORBIDDEN_SUFFIXES:
            forbidden.append(str(rel))
    if forbidden:
        joined = "\n".join(f"  - {item}" for item in forbidden[:40])
        raise SystemExit(f"Forbidden files found in package:\n{joined}")

    required = [package_dir / "SKILL.md", package_dir / "requirements.txt"]
    missing = [str(path.relative_to(package_dir)) for path in required if not path.exists()]
    if missing:
        raise SystemExit(f"Missing required package files: {', '.join(missing)}")


def build(output_root: Path, make_zip: bool) -> Path:
    repo_root = Path(__file__).resolve().parents[1]
    package_dir = output_root / SKILL_NAME

    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir(parents=True)

    for rel in ROOT_FILES:
        shutil.copy2(repo_root / rel, package_dir / rel)

    for rel in ROOT_DIRS:
        src = repo_root / rel
        if src.exists():
            shutil.copytree(src, package_dir / rel, ignore=ignored)

    assert_clean_package(package_dir)

    if make_zip:
        archive_base = output_root / SKILL_NAME
        archive = shutil.make_archive(str(archive_base), "zip", output_root, SKILL_NAME)
        print(f"Wrote {archive}")

    print(f"Wrote {package_dir}")
    return package_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a clean xiaozhua-divination skill package.")
    parser.add_argument("--out", type=Path, default=Path("dist"), help="Output root directory.")
    parser.add_argument("--no-zip", action="store_true", help="Do not create a zip archive.")
    args = parser.parse_args()

    build(args.out, make_zip=not args.no_zip)


if __name__ == "__main__":
    main()
