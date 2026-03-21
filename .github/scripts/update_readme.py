"""
Auto-update script: fetches ALL of Sachith-02's public repos from GitHub API
and rewrites the <!--PROJECTS_START--> ... <!--PROJECTS_END--> block in README.md.

- Shows ALL repos (no language filter, no fork exclusion)
- Language badge shown when available, skipped gracefully if not
- Shows live star count and last updated date per repo
- Sorted by most recently updated
"""

import os
import re
import requests
from datetime import datetime

USERNAME = os.environ.get("GITHUB_USERNAME", "Sachith-02")
TOKEN    = os.environ.get("GITHUB_TOKEN", "")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
}

LANG_BADGES = {
    "Java":       "![Java](https://img.shields.io/badge/-Java-ED8B00?style=flat-square&logo=openjdk&logoColor=white)",
    "C":          "![C](https://img.shields.io/badge/-C-00599C?style=flat-square&logo=c&logoColor=white)",
    "TypeScript": "![TypeScript](https://img.shields.io/badge/-TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)",
    "JavaScript": "![JavaScript](https://img.shields.io/badge/-JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)",
    "Python":     "![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white)",
    "Dart":       "![Dart](https://img.shields.io/badge/-Dart-0175C2?style=flat-square&logo=dart&logoColor=white)",
    "HTML":       "![HTML](https://img.shields.io/badge/-HTML-E34F26?style=flat-square&logo=html5&logoColor=white)",
    "CSS":        "![CSS](https://img.shields.io/badge/-CSS-1572B6?style=flat-square&logo=css3&logoColor=white)",
    "Shell":      "![Shell](https://img.shields.io/badge/-Shell-4EAA25?style=flat-square&logo=gnubash&logoColor=white)",
    "Kotlin":     "![Kotlin](https://img.shields.io/badge/-Kotlin-7F52FF?style=flat-square&logo=kotlin&logoColor=white)",
    "Go":         "![Go](https://img.shields.io/badge/-Go-00ADD8?style=flat-square&logo=go&logoColor=white)",
}

ICON_MAP = {
    "library": "📚", "book": "📖", "core": "⚙️", "api": "🔌",
    "auth": "🔐", "game": "🎲", "yahtzee": "🎲", "sustain": "🌱",
    "insight": "🌱", "weather": "☀️", "travel": "🌍", "chat": "💬",
    "shop": "🛒", "store": "🛒", "blog": "✍️", "todo": "✅",
    "task": "📋", "log": "📝", "note": "📝", "test": "🧪",
    "demo": "🎬", "micro": "💼", "saas": "💼",
}

def get_icon(name):
    lower = name.lower()
    for keyword, icon in ICON_MAP.items():
        if keyword in lower:
            return icon
    return "🔹"

def fetch_all_repos():
    all_repos = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{USERNAME}/repos"
        params = {"sort": "updated", "per_page": 100, "page": page, "type": "public"}
        resp = requests.get(url, headers=HEADERS, params=params)
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        all_repos.extend(batch)
        page += 1
    return all_repos

def format_date(iso_str):
    try:
        dt = datetime.strptime(iso_str[:10], "%Y-%m-%d")
        return dt.strftime("%b %d, %Y")
    except Exception:
        return iso_str[:10]

def build_card(repo):
    name     = repo.get("name", "")
    desc     = repo.get("description") or "No description provided."
    url      = repo.get("html_url", "")
    language = repo.get("language") or ""
    updated  = format_date(repo.get("updated_at", ""))
    is_fork  = repo.get("fork", False)

    icon        = get_icon(name)
    lang_badge  = LANG_BADGES.get(language, f"![{language}](https://img.shields.io/badge/-{language.replace(' ', '_')}-555?style=flat-square)" if language else "")
    stars_badge = f"![Stars](https://img.shields.io/github/stars/{USERNAME}/{name}?style=flat-square&color=38bdf8&labelColor=0d1117)"
    fork_note   = " *(fork)*" if is_fork else ""

    return f"""<td width="50%">

**{icon} {name}**{fork_note}
> {desc}

{lang_badge} {stars_badge}
<sub>🕒 Updated: {updated}</sub>

[![Repo](https://img.shields.io/badge/View_Repo-0d1117?style=for-the-badge&logo=github&logoColor=38bdf8)]({url})

</td>"""

def build_projects_section(repos):
    if not repos:
        return "<!--PROJECTS_START-->\n### 🚀 My Repositories\n\n*No public repositories yet.*\n\n<!--PROJECTS_END-->"

    cards = [build_card(r) for r in repos]

    rows = []
    for i in range(0, len(cards), 2):
        pair = cards[i:i+2]
        if len(pair) == 1:
            pair.append('<td width="50%"></td>')
        rows.append("<tr>\n" + "\n".join(pair) + "\n</tr>")

    last_updated = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    table = (
        '<div align="center">\n<table>\n'
        + "\n".join(rows)
        + '\n</table>\n</div>\n\n'
        + f'<sub align="center">🤖 Auto-updated on {last_updated} · {len(repos)} public repos</sub>'
    )

    return (
        "<!--PROJECTS_START-->\n"
        "### 🚀 My Repositories\n\n"
        "<!-- Auto-updated by GitHub Actions — do not edit this section manually -->\n\n"
        + table
        + "\n\n<!--PROJECTS_END-->"
    )

def update_readme(new_section):
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r"<!--PROJECTS_START-->.*?<!--PROJECTS_END-->"
    updated, count = re.subn(pattern, new_section, content, flags=re.DOTALL)

    if count == 0:
        print("Warning: markers not found — appending section.")
        updated = content.rstrip() + "\n\n" + new_section + "\n"

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated)

    print(f"README updated — {count} section(s) replaced.")

if __name__ == "__main__":
    print(f"Fetching ALL public repos for {USERNAME}...")
    repos = fetch_all_repos()
    print(f"Found {len(repos)} public repos")
    section = build_projects_section(repos)
    update_readme(section)
    print("Done!")
