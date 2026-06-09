#!/opt/homebrew/bin/python3
"""Wrapper: run ziwei_chart.py with venv packages available."""
import sys

SKILLS_DIR = "/Users/saken/.openclaw/workspace/skills/xiaozhua-divination"
venv_site = f"{SKILLS_DIR}/scripts/.venv/lib/python3.14/site-packages"
sys.path.insert(0, venv_site)
sys.path.insert(0, f"{SKILLS_DIR}/ziwei-doushu/scripts")

from ziwei_chart import main
main()
