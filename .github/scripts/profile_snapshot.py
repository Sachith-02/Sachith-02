#!/usr/bin/env python3
"""Create static profile snapshot files for auditing and release notes."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
CONFIG = ROOT / "profile.config.json"
DOCS = ROOT / "docs"


def load_config() -> Dict[str, Any]:
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def extract_markers(text: str) -> Dict[str, int]:
    markers = re.findall(r"<!-- ([A-Z_]+)_START -->", text)
    return {marker: text.count(f"<!-- {marker}_START -->") for marker in markers}


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    config = load_config()
    readme = README.read_text(encoding="utf-8")
    workflows = config.get("profile_workflows") or []
    sections = config.get("profile_sections") or []
    marker_counts = extract_markers(readme)
    local_assets = sorted(str(path.relative_to(ROOT)) for path in (ROOT / "assets").glob("*.svg"))
    workflow_files = sorted(str(path.relative_to(ROOT)) for path in (ROOT / ".github" / "workflows").glob("*.yml"))

    snapshot = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "username": config.get("username"),
        "display_name": config.get("display_name"),
        "headline": config.get("headline"),
        "readme_bytes": len(readme.encode("utf-8")),
        "configured_workflows": len(workflows),
        "workflow_files": workflow_files,
        "configured_sections": sections,
        "marker_counts": marker_counts,
        "local_svg_assets": local_assets,
        "featured_repositories": config.get("featured_repositories", []),
        "quality_gates": config.get("quality_gates", []),
    }

    (DOCS / "profile-snapshot.json").write_text(json.dumps(snapshot, indent=2), encoding="utf-8")

    workflow_rows = "\n".join(f"| {item.get('name', 'Workflow')} | `{item.get('file', '-')}` | {item.get('purpose', '-')} |" for item in workflows)
    asset_rows = "\n".join(f"- `{asset}`" for asset in local_assets)
    md = f"""# Profile Snapshot

Generated: **{snapshot['generated_at']}**

| Item | Value |
|---|---:|
| README size | {snapshot['readme_bytes']} bytes |
| Configured workflows | {snapshot['configured_workflows']} |
| Workflow files | {len(workflow_files)} |
| Dynamic markers | {len(marker_counts)} |
| Local SVG assets | {len(local_assets)} |

## Workflow inventory

| Workflow | File | Purpose |
|---|---|---|
{workflow_rows}

## Local SVG assets

{asset_rows}
"""
    (DOCS / "PROFILE_SNAPSHOT.md").write_text(md, encoding="utf-8")
    print("Profile snapshot generated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
