#!/usr/bin/env python3
"""Validate and report health for the profile README automation system."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
CONFIG = ROOT / "profile.config.json"
REPORT = ROOT / "docs" / "PROFILE_HEALTH_REPORT.md"

REQUIRED_MARKERS = [
    "ABOUT_ME",
    "PROFILE_SUMMARY",
    "ACTIONS_DASHBOARD",
    "ENGINEERING_MATRIX",
    "LANGUAGE_SUMMARY",
    "PROJECT_STATUS",
    "FEATURED_PROJECTS",
    "PROJECTS",
    "REPO_HEALTH",
    "ACTIVITY",
    "AUTOMATION_ARCHITECTURE",
]

REQUIRED_FILES = [
    "README.md",
    "profile.config.json",
    ".github/scripts/update_profile.py",
    ".github/scripts/generate_profile_assets.py",
    ".github/scripts/profile_health_check.py",
    ".github/workflows/update-profile.yml",
    ".github/workflows/test-profile-automation.yml",
    ".github/workflows/validate-profile.yml",
    ".github/workflows/generate-profile-assets.yml",
    ".github/workflows/weekly-profile-maintenance.yml",
    "assets/engineering-matrix.svg",
    "assets/automation-workflow.svg",
]

REQUIRED_CONFIG_KEYS = [
    "username",
    "display_name",
    "headline",
    "current_focus",
    "featured_repositories",
    "project_ci_badges",
    "profile_workflows",
    "engineering_domains",
]


def status(ok: bool) -> str:
    return "✅" if ok else "❌"


def load_config() -> Dict:
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def check_markers(readme_text: str) -> List[Tuple[str, bool, str]]:
    results = []
    for marker in REQUIRED_MARKERS:
        start = f"<!-- {marker}_START -->"
        end = f"<!-- {marker}_END -->"
        ok = start in readme_text and end in readme_text and readme_text.index(start) < readme_text.index(end)
        results.append((f"README marker `{marker}`", ok, "Start/end marker pair present" if ok else "Missing or invalid marker pair"))
    return results


def check_files() -> List[Tuple[str, bool, str]]:
    results = []
    for rel in REQUIRED_FILES:
        path = ROOT / rel
        ok = path.exists()
        results.append((f"File `{rel}`", ok, "Present" if ok else "Missing"))
    return results


def check_config(config: Dict) -> List[Tuple[str, bool, str]]:
    results = []
    for key in REQUIRED_CONFIG_KEYS:
        ok = key in config and config.get(key) not in (None, "", [])
        results.append((f"Config `{key}`", ok, "Configured" if ok else "Missing or empty"))
    workflows = config.get("profile_workflows") or []
    for workflow in workflows:
        file_name = workflow.get("file")
        ok = bool(file_name) and (ROOT / ".github" / "workflows" / file_name).exists()
        results.append((f"Workflow config `{file_name}`", ok, "Workflow file exists" if ok else "Configured workflow file is missing"))
    return results


def build_report(results: List[Tuple[str, bool, str]]) -> str:
    total = len(results)
    passed = sum(1 for _, ok, _ in results if ok)
    score = round((passed / total * 100) if total else 0, 1)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    rows = "\n".join(f"| {status(ok)} | {name} | {detail} |" for name, ok, detail in results)
    return f"""# Profile Automation Health Report

Generated: **{now}**

Overall score: **{score}%**  
Checks passed: **{passed}/{total}**

| Status | Check | Detail |
|---|---|---|
{rows}

## Recommended next steps

1. Keep every dynamic README block inside its `<!-- NAME_START -->` and `<!-- NAME_END -->` markers.
2. Update `profile.config.json` when you add a new flagship repository or workflow.
3. Add topics, descriptions, releases, and CI files to your strongest repositories.
4. Run **Weekly Profile Maintenance** after major project updates.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true", help="Fail when health checks do not pass")
    args = parser.parse_args()

    readme_text = README.read_text(encoding="utf-8") if README.exists() else ""
    config = load_config() if CONFIG.exists() else {}
    results: List[Tuple[str, bool, str]] = []
    results.extend(check_files())
    results.extend(check_markers(readme_text))
    results.extend(check_config(config))

    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text(build_report(results), encoding="utf-8")

    failures = [name for name, ok, _ in results if not ok]
    if failures:
        print("Profile health failures:")
        for item in failures:
            print(f"- {item}")
        return 1 if args.check_only else 0
    print("Profile health checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
