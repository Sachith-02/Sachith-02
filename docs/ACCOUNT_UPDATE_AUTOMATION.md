# Automatic Account-Based About Me Updates

This profile now updates the marked `About Me` block from live GitHub account data.

## What changes automatically

The script reads the GitHub API and rewrites only this safe README block:

```md
<!-- ABOUT_ME_START -->
...
<!-- ABOUT_ME_END -->
```

It can update the section when these public account signals change:

- GitHub display name
- GitHub bio
- GitHub location
- public repository count
- follower and following counts
- total stars and forks across public repositories
- strongest active repository
- most recently updated repository
- main repository languages
- latest public activity

Keep any manual writing that should never be overwritten outside the marked block.

## Update modes

### 1. Automatic scheduled update

The main workflow runs every 6 hours:

```yaml
schedule:
  - cron: "15 */6 * * *"
```

This is the simplest and safest method. If you create a repo, edit a repo description, get followers, publish a release, or update code, the profile will refresh on the next scheduled run.

### 2. Manual update

Go to:

`GitHub profile repo → Actions → Advanced Profile Automation → Run workflow`

Use this when you want the README updated immediately after a major change.

### 3. Optional instant update from other repositories

The workflow also supports this event:

```yaml
repository_dispatch:
  types: [profile-update]
```

To make a project repository trigger your profile update immediately after a push or release, copy this file into that project:

```text
docs/templates/trigger-profile-update.yml
```

Then add a repository secret named `PROFILE_UPDATE_TOKEN` in that project. The token must be able to call the GitHub API for your profile repository.

## Important limitation

GitHub does not automatically send every account-level event to your profile repository. For example, a follower count change may not instantly trigger a workflow. The 6-hour schedule solves this by checking the live API regularly.

For near-instant updates, use the optional `repository_dispatch` template in your important repositories.
