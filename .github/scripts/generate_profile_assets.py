#!/usr/bin/env python3
"""Generate local SVG assets used by the GitHub profile README."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "profile.config.json"
ASSETS_DIR = ROOT / "assets"


def load_config() -> Dict[str, Any]:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def esc(value: Any) -> str:
    return html.escape(str(value or ""), quote=True)


def clamp(value: Any, low: int = 0, high: int = 100) -> int:
    try:
        number = int(float(value))
    except Exception:
        number = 0
    return max(low, min(high, number))


def svg_wrapper(width: int, height: int, content: str) -> str:
    return f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Generated GitHub profile asset">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#020617"/>
      <stop offset="45%" stop-color="#0f172a"/>
      <stop offset="100%" stop-color="#082f49"/>
    </linearGradient>
    <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#38bdf8"/>
      <stop offset="60%" stop-color="#22c55e"/>
      <stop offset="100%" stop-color="#f97316"/>
    </linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="#000000" flood-opacity="0.35"/>
    </filter>
  </defs>
  <rect width="{width}" height="{height}" rx="26" fill="url(#bg)"/>
  <circle cx="{width - 70}" cy="65" r="120" fill="#38bdf8" opacity="0.08"/>
  <circle cx="80" cy="{height - 45}" r="150" fill="#22c55e" opacity="0.07"/>
{content}
</svg>
'''



def generate_profile_banner(config: Dict[str, Any]) -> str:
    width = 1200
    height = 360
    name = esc(config.get("display_name", config.get("username", "Developer")))
    headline = esc(config.get("headline", "Backend Developer"))
    tagline = esc(config.get("tagline", "Building clean software with automation-first engineering habits."))
    focus = config.get("current_focus") or []
    chips = [esc(str(item).split(" and ")[0][:34]) for item in focus[:4]]
    items = [
        '  <text x="60" y="86" fill="#38bdf8" font-family="JetBrains Mono, Consolas, monospace" font-size="16" font-weight="800">BACKEND · AUTOMATION · SYSTEM DESIGN</text>',
        f'  <text x="60" y="145" fill="#f8fafc" font-family="Inter, Segoe UI, Arial" font-size="52" font-weight="900">{name}</text>',
        f'  <text x="62" y="190" fill="#cbd5e1" font-family="Inter, Segoe UI, Arial" font-size="22" font-weight="700">{headline}</text>',
        f'  <text x="62" y="226" fill="#94a3b8" font-family="Inter, Segoe UI, Arial" font-size="16">{tagline}</text>',
        '  <rect x="860" y="62" width="260" height="220" rx="28" fill="#0f172a" opacity="0.88" filter="url(#shadow)"/>',
        '  <text x="892" y="110" fill="#e2e8f0" font-family="Inter, Segoe UI, Arial" font-size="18" font-weight="800">Profile System</text>',
        '  <text x="892" y="145" fill="#38bdf8" font-family="JetBrains Mono, Consolas, monospace" font-size="34" font-weight="900">CI/CD</text>',
        '  <text x="892" y="177" fill="#cbd5e1" font-family="Inter, Segoe UI, Arial" font-size="14">Self-updating README</text>',
        '  <text x="892" y="204" fill="#cbd5e1" font-family="Inter, Segoe UI, Arial" font-size="14">Generated SVG assets</text>',
        '  <text x="892" y="231" fill="#cbd5e1" font-family="Inter, Segoe UI, Arial" font-size="14">Health checks + snapshots</text>',
    ]
    x = 62
    y = 270
    for chip in chips:
        w = 18 + len(chip) * 8
        if x + w > 790:
            break
        items.append(f'  <rect x="{x}" y="{y}" width="{w}" height="34" rx="17" fill="#082f49" stroke="#38bdf8" stroke-opacity="0.38"/>')
        items.append(f'  <text x="{x + 14}" y="{y + 22}" fill="#e0f2fe" font-family="Inter, Segoe UI, Arial" font-size="13" font-weight="700">{chip}</text>')
        x += w + 12
    return svg_wrapper(width, height, "\n".join(items))


def generate_portfolio_roadmap(config: Dict[str, Any]) -> str:
    width = 1100
    height = 340
    roadmap = config.get("portfolio_roadmap") or []
    items = [
        '  <text x="44" y="58" fill="#e2e8f0" font-family="Inter, Segoe UI, Arial" font-size="30" font-weight="800">Portfolio Upgrade Roadmap</text>',
        '  <text x="44" y="88" fill="#94a3b8" font-family="Inter, Segoe UI, Arial" font-size="15">Clean profile growth plan generated from profile.config.json</text>',
    ]
    x = 56
    y = 145
    card_w = 238
    gap = 22
    for index, item in enumerate(roadmap[:4]):
        stage = esc(item.get("stage", f"Step {index + 1}"))
        goal = esc(item.get("goal", "Improve portfolio"))[:34]
        deliverable = esc(item.get("deliverable", "Documented deliverable"))[:44]
        items.append(f'  <rect x="{x}" y="{y}" width="{card_w}" height="128" rx="22" fill="#0f172a" opacity="0.9" filter="url(#shadow)"/>')
        items.append(f'  <text x="{x + 24}" y="{y + 38}" fill="#38bdf8" font-family="JetBrains Mono, Consolas, monospace" font-size="15" font-weight="900">{stage}</text>')
        items.append(f'  <text x="{x + 24}" y="{y + 72}" fill="#f8fafc" font-family="Inter, Segoe UI, Arial" font-size="16" font-weight="800">{goal}</text>')
        items.append(f'  <text x="{x + 24}" y="{y + 100}" fill="#94a3b8" font-family="Inter, Segoe UI, Arial" font-size="12">{deliverable}</text>')
        if index < min(len(roadmap),4) - 1:
            items.append(f'  <path d="M {x + card_w + 5} {y + 64} H {x + card_w + gap - 5}" stroke="#38bdf8" stroke-width="3" stroke-linecap="round" opacity="0.65"/>')
        x += card_w + gap
    return svg_wrapper(width, height, "\n".join(items))

def generate_engineering_matrix(config: Dict[str, Any]) -> str:
    domains: List[Dict[str, Any]] = config.get("engineering_domains") or []
    width = 1100
    row_h = 54
    height = 132 + row_h * max(len(domains), 1)
    items = [
        '  <text x="44" y="58" fill="#e2e8f0" font-family="Inter, Segoe UI, Arial" font-size="30" font-weight="800">Engineering Signal Matrix</text>',
        '  <text x="44" y="88" fill="#94a3b8" font-family="Inter, Segoe UI, Arial" font-size="15">Config-driven skill/evidence board generated by GitHub Actions</text>',
    ]
    y = 126
    for item in domains:
        domain = esc(item.get("domain", "Engineering"))
        level = clamp(item.get("level", 0))
        evidence = esc(item.get("evidence", "Evidence configured in profile.config.json"))
        bar_width = int(360 * level / 100)
        items.append(f'  <rect x="44" y="{y - 30}" width="1012" height="42" rx="14" fill="#0f172a" opacity="0.82" filter="url(#shadow)"/>')
        items.append(f'  <text x="68" y="{y - 4}" fill="#f8fafc" font-family="Inter, Segoe UI, Arial" font-size="16" font-weight="700">{domain}</text>')
        items.append(f'  <rect x="285" y="{y - 18}" width="360" height="12" rx="6" fill="#1e293b"/>')
        items.append(f'  <rect x="285" y="{y - 18}" width="{bar_width}" height="12" rx="6" fill="url(#accent)"/>')
        items.append(f'  <text x="664" y="{y - 5}" fill="#38bdf8" font-family="JetBrains Mono, Consolas, monospace" font-size="15" font-weight="700">{level}%</text>')
        items.append(f'  <text x="735" y="{y - 5}" fill="#cbd5e1" font-family="Inter, Segoe UI, Arial" font-size="13">{evidence}</text>')
        y += row_h
    return svg_wrapper(width, height, "\n".join(items))


def generate_automation_workflow(config: Dict[str, Any]) -> str:
    width = 1100
    height = 360
    steps = [
        ("Trigger", "schedule / push / dispatch"),
        ("Quality Gate", "JSON + tests + markers"),
        ("Assets", "SVG generation"),
        ("GitHub API", "repos + languages + events"),
        ("README", "dynamic block rewrite"),
        ("Commit", "bot pushes update"),
    ]
    items = [
        '  <text x="44" y="58" fill="#e2e8f0" font-family="Inter, Segoe UI, Arial" font-size="30" font-weight="800">Profile Automation Pipeline</text>',
        f'  <text x="44" y="88" fill="#94a3b8" font-family="Inter, Segoe UI, Arial" font-size="15">{len(config.get("profile_workflows") or [])} workflows coordinate validation, generation, maintenance, and release packaging</text>',
    ]
    x = 48
    y = 148
    card_w = 150
    gap = 28
    for index, (title, subtitle) in enumerate(steps):
        items.append(f'  <rect x="{x}" y="{y}" width="{card_w}" height="116" rx="20" fill="#0f172a" opacity="0.9" filter="url(#shadow)"/>')
        items.append(f'  <circle cx="{x + 30}" cy="{y + 30}" r="15" fill="#38bdf8" opacity="0.18"/>')
        items.append(f'  <text x="{x + 24}" y="{y + 36}" fill="#38bdf8" font-family="JetBrains Mono, Consolas, monospace" font-size="16" font-weight="800">{index + 1}</text>')
        items.append(f'  <text x="{x + 20}" y="{y + 70}" fill="#f8fafc" font-family="Inter, Segoe UI, Arial" font-size="17" font-weight="800">{esc(title)}</text>')
        items.append(f'  <text x="{x + 20}" y="{y + 94}" fill="#94a3b8" font-family="Inter, Segoe UI, Arial" font-size="12">{esc(subtitle)}</text>')
        if index < len(steps) - 1:
            ax = x + card_w + 6
            items.append(f'  <path d="M {ax} {y + 58} H {ax + gap - 14}" stroke="#38bdf8" stroke-width="3" stroke-linecap="round" opacity="0.72"/>')
            items.append(f'  <path d="M {ax + gap - 20} {y + 50} L {ax + gap - 10} {y + 58} L {ax + gap - 20} {y + 66}" stroke="#38bdf8" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="0.72"/>')
        x += card_w + gap
    items.append('  <text x="44" y="318" fill="#cbd5e1" font-family="Inter, Segoe UI, Arial" font-size="14">Result: a profile README that behaves like a small production system — tested, scheduled, observable, and self-updating.</text>')
    return svg_wrapper(width, height, "\n".join(items))


def generate_profile_layers(config: Dict[str, Any]) -> str:
    width = 1100
    height = 300
    sections = config.get("profile_sections") or []
    items = [
        '  <text x="44" y="58" fill="#e2e8f0" font-family="Inter, Segoe UI, Arial" font-size="30" font-weight="800">README Module System</text>',
        '  <text x="44" y="88" fill="#94a3b8" font-family="Inter, Segoe UI, Arial" font-size="15">Each module is independently regenerated through comment markers</text>',
    ]
    x = 44
    y = 126
    for i, section in enumerate(sections[:10]):
        w = 196 if i % 3 == 0 else 176
        if x + w > width - 44:
            x = 44
            y += 62
        items.append(f'  <rect x="{x}" y="{y}" width="{w}" height="42" rx="14" fill="#0f172a" opacity="0.9"/>')
        items.append(f'  <text x="{x + 16}" y="{y + 27}" fill="#e2e8f0" font-family="Inter, Segoe UI, Arial" font-size="14" font-weight="700">{esc(section)}</text>')
        x += w + 16
    return svg_wrapper(width, height, "\n".join(items))


def main() -> int:
    config = load_config()
    ASSETS_DIR.mkdir(exist_ok=True)
    outputs = {
        "profile-banner.svg": generate_profile_banner(config),
        "engineering-matrix.svg": generate_engineering_matrix(config),
        "automation-workflow.svg": generate_automation_workflow(config),
        "profile-layers.svg": generate_profile_layers(config),
        "portfolio-roadmap.svg": generate_portfolio_roadmap(config),
    }
    for filename, content in outputs.items():
        (ASSETS_DIR / filename).write_text(content, encoding="utf-8")
        print(f"generated assets/{filename}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
