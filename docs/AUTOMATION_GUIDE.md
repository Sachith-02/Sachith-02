# Advanced GitHub Profile Automation Guide

This profile repository uses GitHub Actions + Python to keep the README dynamic.

## 1. Files

| File | Purpose |
|---|---|
| `README.md` | Main profile page with protected update markers |
| `profile.config.json` | Your editable settings: username, featured repos, filters, limits |
| `.github/scripts/update_profile.py` | Automation script that fetches GitHub data and rewrites sections |
| `.github/workflows/update-profile.yml` | GitHub Actions workflow that tests and runs the script |
| `.github/workflows/test-profile-automation.yml` | CI workflow for the Python automation test suite |
| `tests/test_update_profile.py` | Unit tests for scoring, filtering, badges, release output, and README block replacement |
| `docs/architecture/` | Mermaid architecture diagrams for portfolio projects |
| `docs/REPOSITORY_TOPICS.md` | Recommended topics and GitHub CLI commands |
| `docs/RELEASE_PLAYBOOK.md` | Release checklist and first-release template |
| `docs/ACCOUNT_UPDATE_AUTOMATION.md` | Explains the auto-updating About Me section |
| `docs/templates/trigger-profile-update.yml` | Optional workflow for near-instant profile refreshes from project repositories |

## 2. How it works

The workflow runs in three ways:

1. **Automatically every 6 hours** using a cron schedule.
2. **Manually** from GitHub Actions using `workflow_dispatch`.
3. **After changes** to the README, config, script, tests, or workflow.
4. **Optionally from other repositories** using `repository_dispatch` with the `profile-update` event.

The script updates only these blocks:

- `ABOUT_ME`
- `PROFILE_SUMMARY`
- `LANGUAGE_SUMMARY`
- `PROJECT_STATUS`
- `FEATURED_PROJECTS`
- `PROJECTS`
- `ACTIVITY`

Do not delete these markers unless you also edit the script.

## 3. How to customize featured projects

Open `profile.config.json` and change:

```json
"featured_repositories": [
  "LibraCore",
  "Knowledge-Studio",
  "TaskLang",
  "Distributed_Systems_Group_30"
]
```

Put your strongest repositories first.

## 4. How to show forked repositories

By default, forked repositories are hidden from the portfolio section because original projects are stronger for internship or higher-study applications.

To include forks, change:

```json
"include_forks": true
```

## 5. How to run tests locally

```bash
python -m unittest discover -s tests -v
```

## 6. How to run the profile updater locally

```bash
python .github/scripts/update_profile.py
```

For higher GitHub API limits locally, set a token first:

```bash
export GITHUB_TOKEN="your_token_here"
python .github/scripts/update_profile.py
```

## 7. How to update CI badges

The profile uses `project_ci_badges` in `profile.config.json`. If a project uses a different workflow file, change the value:

```json
{
  "repository": "LibraCore",
  "workflow": "ci.yml",
  "label": "LibraCore CI"
}
```

## 8. How to improve repository tags and releases

- Use `docs/REPOSITORY_TOPICS.md` to add project topics.
- Use `docs/RELEASE_PLAYBOOK.md` to publish a clean first release.
- Copy `docs/templates/ci.yml` into project repositories that do not yet have a CI workflow.


## 9. How the About Me section updates automatically

The `ABOUT_ME` block is generated from live GitHub account and repository data. It can change when your GitHub bio, location, follower count, repository count, top languages, strongest project, latest activity, or most recently updated project changes.

For normal use, the 6-hour schedule is enough. For near-instant updates after pushes or releases in another repository, copy `docs/templates/trigger-profile-update.yml` into that project and configure the `PROFILE_UPDATE_TOKEN` secret.
