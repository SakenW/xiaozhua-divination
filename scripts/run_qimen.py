#!/usr/bin/env python3
"""Run qimen_cli.py with bundled dependencies when present."""
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
for site_packages in sorted((SKILL_DIR / "scripts" / ".venv" / "lib").glob("python*/site-packages")):
    sys.path.insert(0, str(site_packages))
sys.path.insert(0, str(SKILL_DIR / "qimen-dunjia" / "scripts"))

from qimen_cli import main
main()
