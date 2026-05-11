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
    """Fetch recent public GitHub activity events.

    GitHub's public events endpoint can contain event types we do not render,
    so we fetch a wider window and let the README builder pick the best rows.
    """
    try:
        per_page = min(max(limit * 5, 20), 100)
        events = api_get(f"/users/{username}/events/public", {"per_page": per_page})
        return events if isinstance(events, list) else []
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




def fetch_user_profile(username: str) -> Dict[str, Any]:
    """Fetch the public GitHub account profile for the configured username."""
    profile = api_get(f"/users/{username}")
    return profile if isinstance(profile, dict) else {}


def compact_number(value: Any) -> str:
    """Format large GitHub counters in a compact profile-friendly way."""
    try:
        number = int(value or 0)
    except Exception:
        number = 0
    if number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M".replace(".0M", "M")
    if number >= 1_000:
        return f"{number / 1_000:.1f}k".replace(".0k", "k")
    return str(number)


def escape_java_string(value: Any) -> str:
    """Escape generated text before placing it inside the README Java snippet."""
    return str(value or "").replace("\\", "\\\\").replace('"', '\\"')


def get_top_languages_text(language_totals: Dict[str, int], limit: int = 4) -> str:
    languages = list(language_totals.keys())[:limit]
    return ", ".join(languages) if languages else "GitHub language data is still building"


def describe_event_inline(event: Dict[str, Any]) -> str:
    """Convert a public GitHub event into a compact About Me sentence."""
    line = describe_event(event)
    if not line:
        return "No recent public activity detected yet"
    line = re.sub(r"^-\s*", "", line).replace("**", "")
    return line


def build_auto_about_section(
    profile: Dict[str, Any],
    repos: List[Dict[str, Any]],
    language_totals: Dict[str, int],
    events: List[Dict[str, Any]],
    config: Dict[str, Any],
    scores: Optional[Dict[str, RepoScore]] = None,
) -> str:
    """Generate the profile About Me block from live GitHub account data."""
    username = config["username"]
    name = profile.get("name") or config.get("display_name") or username
    location = profile.get("location") or config.get("location") or "Sri Lanka"
    account_bio = profile.get("bio") or config.get("tagline") or "Building practical software projects and improving every repository step by step."
    headline = config.get("headline") or "Software Developer"
    public_repo_count = int(profile.get("public_repos") or len(repos))
    followers = int(profile.get("followers") or 0)
    following = int(profile.get("following") or 0)
    total_stars = sum(int(r.get("stargazers_count") or 0) for r in repos)
    total_forks = sum(int(r.get("forks_count") or 0) for r in repos)
    original_count = sum(1 for r in repos if not r.get("fork"))
    top_languages = get_top_languages_text(language_totals)

    scores = scores or {repo.get("name", ""): score_repo(repo) for repo in repos}
    strongest_repo = None
    if repos:
        strongest_repo = max(repos, key=lambda r: scores.get(r.get("name", ""), score_repo(r)).score)
    recent_repo = None
    if repos:
        recent_repo = max(repos, key=lambda r: parse_iso_datetime(r.get("updated_at", "")))

    strongest_name = strongest_repo.get("name") if strongest_repo else "projects in progress"
    strongest_desc = truncate(strongest_repo.get("description") or "Portfolio project with improving engineering quality.", 105) if strongest_repo else "Portfolio project with improving engineering quality."
    recent_name = recent_repo.get("name") if recent_repo else "repository activity"
    recent_date = format_date(recent_repo.get("updated_at", "")) if recent_repo else "soon"
    latest_activity = describe_event_inline(events[0]) if events else "No recent public activity detected yet"
    focus_items = [str(item) for item in config.get("current_focus", [])[:3]]
    focus_text = "; ".join(focus_items) if focus_items else headline
    primary_focus = focus_items[0] if focus_items else headline
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return f'''<!-- ABOUT_ME_START -->
## 👋 About Me

I am **{escape_md(name)}**, a **{escape_md(headline)}** from **{escape_md(location)}**. This section refreshes automatically from my public GitHub account, repository metadata, languages, and recent activity.

> {escape_md(account_bio)}

- 🔭 GitHub signal: **{compact_number(public_repo_count)} public repositories**, **{compact_number(original_count)} original projects**, **{compact_number(total_stars)} stars**, **{compact_number(total_forks)} forks**, and **{compact_number(followers)} followers**
- 🧠 Main language signal: **{escape_md(top_languages)}**
- 🚀 Strongest active project: **[{escape_md(strongest_name)}](https://github.com/{username}/{strongest_name})** — {escape_md(strongest_desc)}
- 🕒 Most recently updated project: **[{escape_md(recent_name)}](https://github.com/{username}/{recent_name})** · {recent_date}
- ⚡ Latest public activity: {latest_activity}
- 🎯 Current focus: {escape_md(focus_text)}

```java
record Developer(String focus, String githubSignal, String currentProject) {{}}

var sachith = new Developer(
    "{escape_java_string(primary_focus)}",
    "{original_count} original projects · {total_stars} stars · {followers} followers · {following} following",
    "{escape_java_string(strongest_name)}"
);
```

<sub>🤖 Auto-updated by GitHub Actions from the GitHub API. Last generated: **{now}**.</sub>

<!-- ABOUT_ME_END -->'''

def workflow_badge(username: str, repository: str, workflow: str, label: Optional[str] = None) -> str:
    """Return a GitHub Actions badge for a repository workflow file."""
    workflow_path = urllib.parse.quote(workflow, safe="")
    return (
        f"[![{escape_md(label or repository + ' CI')}]("
        f"https://github.com/{username}/{repository}/actions/workflows/{workflow_path}/badge.svg"
        f")](https://github.com/{username}/{repository}/actions/workflows/{workflow_path})"
    )


def release_badge(username: str, repository: str, label: Optional[str] = None) -> str:
    """Return a Shields.io release badge for a repository."""
    safe_label = urllib.parse.quote(label or f"{repository} release")
    return (
        f"![{escape_md(label or repository + ' release')}]"
        f"(https://img.shields.io/github/v/release/{username}/{repository}"
        f"?include_prereleases&label={safe_label}&logo=github&style=flat-square&color=38bdf8&labelColor=0d1117)"
    )


def build_project_status_section(config: Dict[str, Any]) -> str:
    """Build CI and release badges for the repositories that should stand out first."""
    username = config["username"]
    badge_configs = config.get("project_ci_badges") or []

    if not badge_configs:
        badge_configs = [
            {"repository": repo, "workflow": "ci.yml", "label": f"{repo} CI"}
            for repo in config.get("featured_repositories", [])
        ]

    rows: List[str] = []
    for item in badge_configs:
        repository = item.get("repository")
        workflow = item.get("workflow", "ci.yml")
        if not repository:
            continue
        label = item.get("label") or f"{repository} CI"
        rows.append(
            "| "
            f"[{escape_md(repository)}](https://github.com/{username}/{repository})"
            " | "
            f"{workflow_badge(username, repository, workflow, label)} "
            f"{release_badge(username, repository)}"
            " |"
        )

    body = "\n".join(rows) if rows else "| No project badges configured yet. | Add `project_ci_badges` in `profile.config.json`. |"

    return f"""<!-- PROJECT_STATUS_START -->
## ✅ Project CI & Release Status

> Badges for the strongest repositories. Update the workflow filenames in `profile.config.json` if a project uses a different CI file name.

| Repository | Status |
|---|---|
{body}

<!-- PROJECT_STATUS_END -->"""


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
            release_badge(username, name, "latest release"),
        ]
        if x
    )
    topic_line = ""
    if topics:
        topic_line = "<br/>" + " ".join(f"<code>{escape_md(t)}</code>" for t in topics[:6])
    else:
        topic_line = "<br/><sub>🏷️ Add GitHub topics to improve this card. See <code>docs/REPOSITORY_TOPICS.md</code>.</sub>"

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


def repo_markdown(repo_name: str) -> str:
    """Create a safe Markdown link for a repository name from an event."""
    repo_name = escape_md(repo_name)
    if "/" not in repo_name:
        return f"`{repo_name}`"
    return f"[`{repo_name}`](https://github.com/{repo_name})"


def event_link(payload: Dict[str, Any], fallback_repo: str) -> str:
    """Find the most useful public URL for a GitHub activity event."""
    for key in ("pull_request", "issue", "release", "comment", "forkee"):
        item = payload.get(key)
        if isinstance(item, dict) and item.get("html_url"):
            return item["html_url"]
    if fallback_repo and "/" in fallback_repo:
        return f"https://github.com/{fallback_repo}"
    return ""


def linked_activity(text: str, url: str) -> str:
    """Turn activity text into a Markdown link when a useful URL exists."""
    text = escape_md(text)
    return f"[{text}]({url})" if url else text


def describe_event(event: Dict[str, Any], include_date: bool = True) -> Optional[str]:
    """Convert a public GitHub event into a profile-friendly activity line."""
    event_type = event.get("type", "")
    repo_name = (event.get("repo") or {}).get("name", "")
    created = format_date(event.get("created_at", ""))
    payload = event.get("payload") or {}
    repo = repo_markdown(repo_name)
    url = event_link(payload, repo_name)
    suffix = f" · {created}" if include_date else ""

    if event_type == "PushEvent":
        commits = len(payload.get("commits") or [])
        branch = str(payload.get("ref") or "").replace("refs/heads/", "")
        branch_text = f" to `{escape_md(branch)}`" if branch else ""
        return f"- 🧩 {linked_activity(f'Pushed {commits} commit{'s' if commits != 1 else ''}', url)}{branch_text} in {repo}{suffix}"
    if event_type == "CreateEvent":
        ref_type = payload.get("ref_type", "item")
        ref = payload.get("ref")
        ref_text = f" `{escape_md(ref)}`" if ref else ""
        return f"- ✨ Created **{escape_md(ref_type)}**{ref_text} in {repo}{suffix}"
    if event_type == "PullRequestEvent":
        action = payload.get("action", "updated")
        pr = payload.get("pull_request") or {}
        title = truncate(pr.get("title") or "pull request", 70)
        number = pr.get("number") or payload.get("number")
        number_text = f" #{number}" if number else ""
        return f"- 🔀 {linked_activity(f'{str(action).capitalize()} PR{number_text}: {title}', url)} in {repo}{suffix}"
    if event_type == "IssuesEvent":
        action = payload.get("action", "updated")
        issue = payload.get("issue") or {}
        title = truncate(issue.get("title") or "issue", 70)
        number = issue.get("number")
        number_text = f" #{number}" if number else ""
        return f"- 📝 {linked_activity(f'{str(action).capitalize()} issue{number_text}: {title}', url)} in {repo}{suffix}"
    if event_type == "IssueCommentEvent":
        action = payload.get("action", "commented on")
        issue = payload.get("issue") or {}
        title = truncate(issue.get("title") or "issue discussion", 70)
        return f"- 💬 {linked_activity(f'{str(action).capitalize()} a comment: {title}', url)} in {repo}{suffix}"
    if event_type == "PullRequestReviewEvent":
        action = payload.get("action", "reviewed")
        pr = payload.get("pull_request") or {}
        title = truncate(pr.get("title") or "pull request", 70)
        return f"- 👀 {linked_activity(f'{str(action).capitalize()} a pull request review: {title}', url)} in {repo}{suffix}"
    if event_type == "PullRequestReviewCommentEvent":
        pr = payload.get("pull_request") or {}
        title = truncate(pr.get("title") or "pull request", 70)
        return f"- 💭 {linked_activity(f'Commented on PR review: {title}', url)} in {repo}{suffix}"
    if event_type == "WatchEvent":
        return f"- ⭐ Starred {repo}{suffix}"
    if event_type == "ForkEvent":
        return f"- 🍴 {linked_activity('Forked repository', url)} from {repo}{suffix}"
    if event_type == "ReleaseEvent":
        action = payload.get("action", "published")
        release = payload.get("release") or {}
        tag = release.get("tag_name")
        tag_text = f" `{escape_md(tag)}`" if tag else ""
        return f"- 🚢 {linked_activity(f'{str(action).capitalize()} release', url)}{tag_text} in {repo}{suffix}"
    if event_type == "PublicEvent":
        return f"- 🌍 Made {repo} public{suffix}"
    if event_type == "GollumEvent":
        pages = payload.get("pages") or []
        count = len(pages)
        return f"- 📚 Updated **{count} wiki page{'s' if count != 1 else ''}** in {repo}{suffix}"
    if event_type == "CommitCommentEvent":
        return f"- 💬 {linked_activity('Commented on a commit', url)} in {repo}{suffix}"
    return None


def build_activity_section(events: List[Dict[str, Any]], max_items: int = 6) -> str:
    rows: List[str] = []
    for event in events:
        line = describe_event(event)
        if not line:
            continue
        rows.append(line)
        if len(rows) >= max_items:
            break

    if rows:
        body = "\n".join(rows)
    else:
        body = "No recent public activity detected by the GitHub Events API."

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"""<!-- ACTIVITY_START -->
## ⚡ Recent Public Activity

> Auto-updated from GitHub public events. Private activity cannot appear here.

{body}

<sub>Last activity refresh: **{now}**</sub>

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

    print(f"Fetching GitHub profile and repositories for {username}...")
    profile = fetch_user_profile(username)
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
    content = replace_block(content, "ABOUT_ME", build_auto_about_section(profile, visible_repos, language_totals, events, config, scores))
    content = replace_block(content, "PROFILE_SUMMARY", build_summary_section(all_repos, language_totals, config))
    content = replace_block(content, "LANGUAGE_SUMMARY", build_language_section(language_totals))
    content = replace_block(content, "PROJECT_STATUS", build_project_status_section(config))
    content = replace_block(content, "FEATURED_PROJECTS", build_featured_section(visible_repos, config, scores))
    content = replace_block(content, "PROJECTS", build_projects_section(visible_repos, config, scores))
    content = replace_block(content, "ACTIVITY", build_activity_section(events, int(config.get("max_recent_activity", 6))))

    README_PATH.write_text(content, encoding="utf-8")
    print("README.md updated successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
