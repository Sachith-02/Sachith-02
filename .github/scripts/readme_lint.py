#!/usr/bin/env python3
"""Professional README lint checks for the profile repository."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"

REQUIRED_SECTIONS = [
    "About Me",
    "Professional Focus",
    "Featured Engineering Projects",
    "Recent Public Activity",
    "Automation Architecture",
]

REQUIRED_MARKERS = [
    "ABOUT_ME",
    "PROFILE_SUMMARY",
    "FOCUS_AREAS",
    "ACTIONS_DASHBOARD",
    "ENGINEERING_MATRIX",
    "LANGUAGE_SUMMARY",
    "PROJECT_STATUS",
    "FEATURED_PROJECTS",
    "PROJECTS",
    "REPO_HEALTH",
    "ACTIVITY",
    "ROADMAP",
    "AUTOMATION_ARCHITECTURE",
]


def fail(message: str, failures: List[str]) -> None:
    failures.append(message)


def local_images(markdown: str) -> List[str]:
    results = []
    for match in re.finditer(r'<img[^>]+src="([^"]+)"', markdown):
        src = match.group(1)
        if src.startswith(("http://", "https://", "data:")):
            continue
        results.append(src)
    return results


def main() -> int:
    failures: List[str] = []
    if not README.exists():
        print("README.md is missing")
        return 1

    text = README.read_text(encoding="utf-8")

    if len(text) < 3500:
        fail("README is too short for a professional profile.", failures)

    for section in REQUIRED_SECTIONS:
        if section not in text:
            fail(f"Missing professional section: {section}", failures)

    for marker in REQUIRED_MARKERS:
        start = f"<!-- {marker}_START -->"
        end = f"<!-- {marker}_END -->"
        if start not in text or end not in text:
            fail(f"Missing marker pair for {marker}", failures)
        elif text.index(start) > text.index(end):
            fail(f"Marker pair is reversed for {marker}", failures)

    headings = re.findall(r"^#{1,3}\s+(.+)$", text, flags=re.MULTILINE)
    duplicates = sorted({h for h in headings if headings.count(h) > 1})
    if duplicates:
        fail(f"Duplicate headings found: {', '.join(duplicates)}", failures)

    for image in local_images(text):
        path = ROOT / image
        if not path.exists():
            fail(f"Local README image does not exist: {image}", failures)

    if "Updating soon" in text:
        fail("README still contains the low-quality placeholder phrase 'Updating soon'.", failures)

    if text.count("github-readme-stats.vercel.app") > 2:
        fail("Too many external stats cards; keep the README clean.", failures)

    if failures:
        print("README lint failed:")
        for item in failures:
            print(f"- {item}")
        return 1

    print("README lint passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
