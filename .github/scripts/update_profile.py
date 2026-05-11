#!/usr/bin/env python3
"""
Advanced GitHub profile README automation.

What it does:
- Fetches live GitHub profile, repository, language, and public activity data.
- Scores repositories using engineering-signalling factors.
- Rewrites only marked README blocks, keeping the rest editable.
- Uses only Python standard library, so the workflow is faster and simpler.

Required files:
- README.md
- profile.config.json

Optional environment variables:
- GITHUB_TOKEN: improves API rate limits during GitHub Actions runs.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "profile.config.json"
README_PATH = ROOT / "README.md"
API_BASE = "https://api.github.com"

LANGUAGE_COLORS = {
    "Java": "ED8B00",
    "C": "00599C",
    "C++": "00599C",
    "Python": "3776AB",
    "TypeScript": "3178C6",
    "JavaScript": "F7DF1E",
    "HTML": "E34F26",
    "CSS": "1572B6",
    "Shell": "4EAA25",
    "Dockerfile": "2496ED",
    "Kotlin": "7F52FF",
    "Go": "00ADD8",
    "Dart": "0175C2",
    "Yacc": "555555",
}

LANGUAGE_LOGOS = {
    "Java": "openjdk",
    "C": "c",
    "C++": "cplusplus",
    "Python": "python",
    "TypeScript": "typescript",
    "JavaScript": "javascript",
    "HTML": "html5",
    "CSS": "css3",
    "Shell": "gnubash",
    "Dockerfile": "docker",
    "Kotlin": "kotlin",
    "Go": "go",
    "Dart": "dart",
}

ICON_MAP = {
    "library": "📚",
    "book": "📖",
    "core": "⚙️",
    "api": "🔌",
    "auth": "🔐",
    "game": "🎲",
    "yahtzee": "🎲",
    "sustain": "🌱",
    "insight": "🌱",
    "knowledge": "🧠",
    "rag": "🧠",
    "weather": "☀️",
    "travel": "🌍",
    "chat": "💬",
    "shop": "🛒",
    "store": "🛒",
    "blog": "✍️",
    "todo": "✅",
    "task": "📋",
    "parser": "🧩",
    "compiler": "🧩",
    "distributed": "🌐",
    "message": "📨",
    "platform": "🚀",
    "frontend": "🎨",
    "backend": "🧱",
}


@dataclass(frozen=True)
class RepoScore:
    name: str
    score: float
    reasons: List[str]


def load_config() -> Dict[str, Any]:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Missing config file: {CONFIG_PATH}")
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def github_headers() -> Dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "advanced-profile-readme-bot",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def api_get(path: str, params: Optional[Dict[str, Any]] = None, retries: int = 3) -> Any:
    query = urllib.parse.urlencode(params or {})
    url = f"{API_BASE}{path}"
    if query:
        url = f"{url}?{query}"

    request = urllib.request.Request(url, headers=github_headers())
    last_error: Optional[Exception] = None

    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = response.read().decode("utf-8")
                return json.loads(payload) if payload else None
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code in {403, 429, 500, 502, 503, 504} and attempt < retries:
                time.sleep(2 * attempt)
                continue
            details = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"GitHub API error {exc.code} for {path}: {details}") from exc
        except Exception as exc:  # network or JSON parsing
            last_error = exc
            if attempt < retries:
                time.sleep(2 * attempt)
                continue
            raise

    raise RuntimeError(f"GitHub API request failed for {path}: {last_error}")


def fetch_repositories(username: str) -> List[Dict[str, Any]]:
    repos: List[Dict[str, Any]] = []
    page = 1
    while True:
        batch = api_get(
            f"/users/{username}/repos",
            {
                "type": "public",
                "sort": "updated",
                "direction": "desc",
                "per_page": 100,
                "page": page,
            },
        )
        if not batch:
            break
        repos.extend(batch)
        page += 1
    return repos


def fetch_languages(username: str, repo_name: str) -> Dict[str, int]:
    return api_get(f"/repos/{username}/{repo_name}/languages") or {}


def fetch_events(username: str, limit: int) -> List[Dict[str, Any]]:
    try:
        events = api_get(f"/users/{username}/events/public", {"per_page": min(max(limit * 3, 10), 30)})
        return events[:limit] if isinstance(events, list) else []
    except Exception as exc:
        print(f"Warning: could not fetch activity events: {exc}", file=sys.stderr)
        return []


def parse_iso_datetime(value: str) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def format_date(value: str) -> str:
    try:
        return parse_iso_datetime(value).strftime("%b %d, %Y")
    except Exception:
        return value[:10] if value else "Unknown"


def days_since(value: str) -> int:
    try:
        return max(0, (datetime.now(timezone.utc) - parse_iso_datetime(value)).days)
    except Exception:
        return 9999


def escape_md(value: Any) -> str:
    text = str(value or "")
    return text.replace("|", "\\|").replace("\n", " ").strip()


def truncate(text: str, limit: int = 145) -> str:
    text = " ".join(str(text or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def get_icon(repo_name: str, description: str = "") -> str:
    searchable = f"{repo_name} {description}".lower()
    for keyword, icon in ICON_MAP.items():
        if keyword in searchable:
            return icon
    return "🔹"


def language_badge(language: str) -> str:
    if not language:
        return ""
    color = LANGUAGE_COLORS.get(language, "555555")
    logo = LANGUAGE_LOGOS.get(language, "")
    logo_part = f"&logo={urllib.parse.quote(logo)}&logoColor=white" if logo else ""
    label = urllib.parse.quote(language.replace("-", "--"))
    text_color = "black" if language == "JavaScript" else "white"
    return f"![{language}](https://img.shields.io/badge/-{label}-{color}?style=flat-square{logo_part}&logoColor={text_color})"


def progress_bar(percent: float, width: int = 18) -> str:
    filled = int(round((percent / 100) * width))
    filled = min(max(filled, 0), width)
    return "█" * filled + "░" * (width - filled)


def score_repo(repo: Dict[str, Any]) -> RepoScore:
    name = repo.get("name", "")
    description = repo.get("description") or ""
    stars = int(repo.get("stargazers_count") or 0)
    forks = int(repo.get("forks_count") or 0)
    topics = repo.get("topics") or []
    fork = bool(repo.get("fork"))
    language = repo.get("language") or ""
    age_days = days_since(repo.get("updated_at", ""))

    score = 0.0
    reasons: List[str] = []

    if not fork:
        score += 18
        reasons.append("original")
    else:
        score -= 12
        reasons.append("fork")

    if description:
        score += 12
        reasons.append("documented")

    if language:
        score += 6
        reasons.append(language)

    if topics:
        score += min(len(topics) * 2, 8)
        reasons.append("topics")

    score += min(stars * 4, 24)
    score += min(forks * 2, 10)

    if age_days <= 7:
        score += 18
        reasons.append("active this week")
    elif age_days <= 30:
        score += 14
        reasons.append("active this month")
    elif age_days <= 90:
        score += 9
    elif age_days <= 365:
        score += 5

    strong_terms = [
        "spring",
        "api",
        "docker",
        "security",
        "jwt",
        "distributed",
        "rag",
        "parser",
        "bison",
        "backend",
        "database",
    ]
    combined = f"{name} {description}".lower()
    for term in strong_terms:
        if term in combined:
            score += 3

    return RepoScore(name=name, score=round(score, 2), reasons=reasons[:4])


def filter_repos(repos: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
    excluded = set(config.get("exclude_repositories", []))
    include_forks = bool(config.get("include_forks", False))
    clean = []
    for repo in repos:
        if repo.get("name") in excluded:
            continue
        if repo.get("archived"):
            continue
        if repo.get("fork") and not include_forks:
            continue
        clean.append(repo)
    return clean


def build_summary_section(repos: List[Dict[str, Any]], language_totals: Dict[str, int], config: Dict[str, Any]) -> str:
    username = config["username"]
    original_count = sum(1 for r in repos if not r.get("fork"))
    fork_count = sum(1 for r in repos if r.get("fork"))
    total_stars = sum(int(r.get("stargazers_count") or 0) for r in repos)
    total_forks = sum(int(r.get("forks_count") or 0) for r in repos)
    top_languages = ", ".join(list(language_totals.keys())[:5]) or "Not detected yet"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return f"""<!-- PROFILE_SUMMARY_START -->
## 🧠 Live Engineering Snapshot

> This block is automatically regenerated by GitHub Actions from live GitHub API data.

| Metric | Value |
|---|---:|
| Public repositories scanned | **{len(repos)}** |
| Original projects | **{original_count}** |
| Forked projects | **{fork_count}** |
| Total stars | **{total_stars}** |
| Total forks | **{total_forks}** |
| Most used languages | **{escape_md(top_languages)}** |
| Automation mode | **Daily schedule + manual workflow dispatch** |
| Last automation run | **{now}** |

![Automation](https://img.shields.io/badge/README-Auto_Updated-38bdf8?style=for-the-badge&logo=githubactions&logoColor=white)
![Repos](https://img.shields.io/badge/Public_Repos-{len(repos)}-0d1117?style=for-the-badge&logo=github&logoColor=white)
![Stars](https://img.shields.io/badge/Total_Stars-{total_stars}-38bdf8?style=for-the-badge&logo=github&logoColor=white)

<!-- PROFILE_SUMMARY_END -->"""


def build_language_section(language_totals: Dict[str, int]) -> str:
    total = sum(language_totals.values())
    if total <= 0:
        body = "No repository language data detected yet."
    else:
        rows = []
        for language, amount in list(language_totals.items())[:8]:
            percent = amount / total * 100
            badge = language_badge(language)
            rows.append(f"{badge} `{progress_bar(percent)}` **{percent:.1f}%**")
        body = "  \n".join(rows)

    return f"""<!-- LANGUAGE_SUMMARY_START -->
## 📌 Language Intelligence

> Automatically calculated from repository language byte data.

{body}

<!-- LANGUAGE_SUMMARY_END -->"""


def repo_card(repo: Dict[str, Any], username: str, score: Optional[RepoScore] = None) -> str:
    name = repo.get("name", "")
    description = truncate(repo.get("description") or "No description provided.")
    html_url = repo.get("html_url") or f"https://github.com/{username}/{name}"
    language = repo.get("language") or ""
    stars = int(repo.get("stargazers_count") or 0)
    forks = int(repo.get("forks_count") or 0)
    updated = format_date(repo.get("updated_at", ""))
    topics = repo.get("topics") or []
    icon = get_icon(name, description)
    badge_line = " ".join(
        x
        for x in [
            language_badge(language),
            f"![Stars](https://img.shields.io/github/stars/{username}/{name}?style=flat-square&color=38bdf8&labelColor=0d1117)",
            f"![Forks](https://img.shields.io/github/forks/{username}/{name}?style=flat-square&color=94a3b8&labelColor=0d1117)",
        ]
        if x
    )
    topic_line = ""
    if topics:
        topic_line = "<br/>" + " ".join(f"<code>{escape_md(t)}</code>" for t in topics[:5])

    score_line = ""
    if score:
        reasons = ", ".join(score.reasons) if score.reasons else "portfolio signal"
        score_line = f"<br/><sub>🧮 Portfolio score: <b>{score.score}</b> · {escape_md(reasons)}</sub>"

    return f"""<td width="50%" valign="top">

### {icon} [{escape_md(name)}]({html_url})

{badge_line}

{description}

<sub>⭐ {stars} stars · 🍴 {forks} forks · 🕒 Updated {updated}</sub>{score_line}{topic_line}

</td>"""


def build_table(cards: List[str]) -> str:
    if not cards:
        return "No repositories to show yet."
    rows = []
    for i in range(0, len(cards), 2):
        pair = cards[i : i + 2]
        if len(pair) == 1:
            pair.append('<td width="50%"></td>')
        rows.append("<tr>\n" + "\n".join(pair) + "\n</tr>")
    return "<div align=\"center\">\n<table>\n" + "\n".join(rows) + "\n</table>\n</div>"


def build_featured_section(repos: List[Dict[str, Any]], config: Dict[str, Any], scores: Dict[str, RepoScore]) -> str:
    username = config["username"]
    priority = config.get("featured_repositories", [])
    repo_by_name = {r.get("name"): r for r in repos}
    selected: List[Dict[str, Any]] = []

    for name in priority:
        repo = repo_by_name.get(name)
        if repo and repo not in selected:
            selected.append(repo)

    max_featured = int(config.get("max_featured_cards", 4))
    if len(selected) < max_featured:
        ranked = sorted(repos, key=lambda r: scores[r.get("name", "")].score, reverse=True)
        for repo in ranked:
            if repo not in selected:
                selected.append(repo)
            if len(selected) >= max_featured:
                break

    cards = [repo_card(repo, username, scores.get(repo.get("name", ""))) for repo in selected[:max_featured]]

    return f"""<!-- FEATURED_PROJECTS_START -->
## 🌟 Featured Engineering Projects

> Selected automatically from configured priority projects and live repository scoring.

{build_table(cards)}

<!-- FEATURED_PROJECTS_END -->"""


def build_projects_section(repos: List[Dict[str, Any]], config: Dict[str, Any], scores: Dict[str, RepoScore]) -> str:
    username = config["username"]
    max_cards = int(config.get("max_repo_cards", 12))
    ranked = sorted(repos, key=lambda r: scores[r.get("name", "")].score, reverse=True)
    cards = [repo_card(repo, username, scores.get(repo.get("name", ""))) for repo in ranked[:max_cards]]

    return f"""<!-- PROJECTS_START -->
## 🚀 Repository Portfolio

> Automatically sorted by portfolio score: originality, recency, documentation, language signal, stars, forks, and project keywords.

{build_table(cards)}

<!-- PROJECTS_END -->"""


def describe_event(event: Dict[str, Any]) -> Optional[str]:
    event_type = event.get("type", "")
    repo_name = (event.get("repo") or {}).get("name", "")
    created = format_date(event.get("created_at", ""))
    payload = event.get("payload") or {}

    if event_type == "PushEvent":
        commits = len(payload.get("commits") or [])
        return f"- 🧩 Pushed **{commits} commit{'s' if commits != 1 else ''}** to `{repo_name}` · {created}"
    if event_type == "CreateEvent":
        ref_type = payload.get("ref_type", "item")
        return f"- ✨ Created **{ref_type}** in `{repo_name}` · {created}"
    if event_type == "PullRequestEvent":
        action = payload.get("action", "updated")
        return f"- 🔀 {action.capitalize()} a pull request in `{repo_name}` · {created}"
    if event_type == "IssuesEvent":
        action = payload.get("action", "updated")
        return f"- 📝 {action.capitalize()} an issue in `{repo_name}` · {created}"
    if event_type == "WatchEvent":
        return f"- ⭐ Starred `{repo_name}` · {created}"
    if event_type == "ForkEvent":
        return f"- 🍴 Forked `{repo_name}` · {created}"
    if event_type == "ReleaseEvent":
        action = payload.get("action", "published")
        return f"- 🚢 {action.capitalize()} a release in `{repo_name}` · {created}"
    return None


def build_activity_section(events: List[Dict[str, Any]]) -> str:
    lines = [line for event in events if (line := describe_event(event))]
    body = "\n".join(lines) if lines else "No recent public activity detected by the GitHub Events API."
    return f"""<!-- ACTIVITY_START -->
## ⚡ Recent Public Activity

{body}

<!-- ACTIVITY_END -->"""


def replace_block(content: str, marker: str, new_block: str) -> str:
    pattern = rf"<!-- {marker}_START -->.*?<!-- {marker}_END -->"
    updated, count = re.subn(pattern, new_block, content, flags=re.DOTALL)
    if count == 0:
        print(f"Warning: marker {marker} not found; appending block.", file=sys.stderr)
        return content.rstrip() + "\n\n" + new_block + "\n"
    return updated


def aggregate_languages(username: str, repos: List[Dict[str, Any]], limit: int) -> Dict[str, int]:
    totals: Dict[str, int] = {}
    candidates = sorted(repos, key=lambda r: score_repo(r).score, reverse=True)[:limit]
    for repo in candidates:
        name = repo.get("name")
        if not name:
            continue
        try:
            languages = fetch_languages(username, name)
            for language, amount in languages.items():
                totals[language] = totals.get(language, 0) + int(amount)
        except Exception as exc:
            print(f"Warning: could not fetch languages for {name}: {exc}", file=sys.stderr)
    return dict(sorted(totals.items(), key=lambda item: item[1], reverse=True))


def main() -> int:
    config = load_config()
    username = config["username"]

    print(f"Fetching GitHub repositories for {username}...")
    all_repos = fetch_repositories(username)
    visible_repos = filter_repos(all_repos, config)
    print(f"Found {len(all_repos)} public repos; using {len(visible_repos)} after filtering.")

    scores = {repo.get("name", ""): score_repo(repo) for repo in visible_repos}
    language_totals = aggregate_languages(
        username,
        visible_repos,
        int(config.get("language_scan_limit", 25)),
    )
    events = fetch_events(username, int(config.get("max_recent_activity", 6)))

    content = README_PATH.read_text(encoding="utf-8")
    content = replace_block(content, "PROFILE_SUMMARY", build_summary_section(all_repos, language_totals, config))
    content = replace_block(content, "LANGUAGE_SUMMARY", build_language_section(language_totals))
    content = replace_block(content, "FEATURED_PROJECTS", build_featured_section(visible_repos, config, scores))
    content = replace_block(content, "PROJECTS", build_projects_section(visible_repos, config, scores))
    content = replace_block(content, "ACTIVITY", build_activity_section(events))

    README_PATH.write_text(content, encoding="utf-8")
    print("README.md updated successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
