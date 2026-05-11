# Advanced GitHub Profile Automation Guide

This profile repository uses GitHub Actions + Python to keep the README dynamic.

## 1. Files

| File | Purpose |
|---|---|
| `README.md` | Main profile page with protected update markers |
| `profile.config.json` | Your editable settings: username, featured repos, filters, limits |
| `.github/scripts/update_profile.py` | Automation script that fetches GitHub data and rewrites sections |
| `.github/workflows/update-profile.yml` | GitHub Actions workflow that runs the script |

## 2. How it works

The workflow runs in three ways:

1. **Automatically every day** using a cron schedule.
2. **Manually** from GitHub Actions using `workflow_dispatch`.
3. **After changes** to the README, config, script, or workflow.

The script updates only these blocks:

- `PROFILE_SUMMARY`
- `LANGUAGE_SUMMARY`
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

## 5. How to run locally

```bash
python .github/scripts/update_profile.py
```

For higher GitHub API limits locally, set a token first:

```bash
export GITHUB_TOKEN="your_token_here"
python .github/scripts/update_profile.py
```

## 6. Good next improvements

- Add tests for the Python script.
- Add project-specific CI badges from your strongest repositories.
- Add architecture diagrams for backend projects.
- Add `topics` to your GitHub repositories so the profile can show better tags.
- Add releases to major projects so activity looks more professional.
