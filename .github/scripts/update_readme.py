"""
Auto-update script: fetches Sachith-02's latest public repos from GitHub API
and rewrites the <!--PROJECTS_START--> ... <!--PROJECTS_END--> block in README.md
"""

import os
import requests

USERNAME = os.environ.get("GITHUB_USERNAME", "Sachith-02")
TOKEN    = os.environ.get("GITHUB_TOKEN", "")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
}

# Map language names to badge styles
LANG_BADGES = {
    "Java":       "![Java](https://img.shields.io/badge/-Java-ED8B00?style=flat-square&logo=openjdk&logoColor=white)",
    "TypeScript": "![TypeScript](https://img.shields.io/badge/-TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)",
    "JavaScript": "![JavaScript](https://img.shields.io/badge/-JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)",
    "C":          "![C](https://img.shields.io/badge/-C-00599C?style=flat-square&logo=c&logoColor=white)",
    "Python":     "![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white)",
    "Dart":       "![Dart](https://img.shields.io/badge/-Dart-0175C2?style=flat-square&logo=dart&logoColor=white)",
    "HTML":       "![HTML](https://img.shields.io/badge/-HTML-E34F26?style=flat-square&logo=html5&logoColor=white)",
    "CSS":        "![CSS](https://img.shields.io/badge/-CSS-1572B6?style=flat-square&logo=css3&logoColor=white)",
}


def fetch_repos():
    url = f"https://api.github.com/users/{USERNAME}/repos"
    params = {"sort": "updated", "per_page": 8, "type": "owner"}
    resp = requests.get(url, headers=HEADERS, params=params)
    resp.raise_for_status()
    repos = [r for r in resp.json() if not r.get("fork")]
    return repos[:6]  # max 6 featured


def build_project_card(repo):
    name     = repo.get("name", "")
    desc     = repo.get("description") or "No description provided."
    url      = repo.get("html_url", "")
    language = repo.get("language") or ""
    stars    = repo.get("stargazers_count", 0)
    updated  = repo.get("updated_at", "")[:10]

    lang_badge = LANG_BADGES.get(language, f"![{language}](https://img.shields.io/badge/-{language}-555?style=flat-square)" if language else "")
    stars_badge = f"![Stars](https://img.shields.io/github/stars/{USERNAME}/{name}?style=flat-square&color=38bdf8&labelColor=0d1117)"

    card = f"""<td width="50%">

**🔹 {name}**
> {desc}

{lang_badge} {stars_badge}

[![Repo](https://img.shields.io/badge/View_Repo-0d1117?style=for-the-badge&logo=github&logoColor=38bdf8)]({url})

</td>"""
    return card


def build_projects_section(repos):
    cards = [build_project_card(r) for r in repos]

    # Pair cards into rows of 2
    rows = []
    for i in range(0, len(cards), 2):
        pair = cards[i:i+2]
        if len(pair) == 1:
            pair.append("<td width=\"50%\"></td>")
        rows.append(f"<tr>\n{pair[0]}\n{pair[1]}\n</tr>")

    table = "<div align=\"center\">\n<table>\n" + "\n".join(rows) + "\n</table>\n</div>"

    section = f"""<!--PROJECTS_START-->
### 🚀 Featured Projects

{table}
<!--PROJECTS_END-->"""
    return section


def update_readme(new_section):
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    import re
    pattern = r"<!--PROJECTS_START-->.*?<!--PROJECTS_END-->"
    updated = re.sub(pattern, new_section, content, flags=re.DOTALL)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated)

    print("✅ README updated successfully.")


if __name__ == "__main__":
    print(f"🔍 Fetching repos for {USERNAME}...")
    repos = fetch_repos()
    print(f"📦 Found {len(repos)} repos")
    section = build_projects_section(repos)
    update_readme(section)
