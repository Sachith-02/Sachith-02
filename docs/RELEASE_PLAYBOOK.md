# Release Playbook for Major Projects

A visible release history makes a GitHub project look more mature because it shows versions, milestones, and maintenance discipline.

## Suggested release order

1. `LibraCore` — first release should focus on backend API, authentication, database setup, and Docker instructions.
2. `Knowledge-Studio` — first release should show document ingestion, search/query flow, and example outputs.
3. `TaskLang` — first release should show language syntax, parser/compiler features, and CLI usage.
4. `Distributed_Systems_Group_30` — first release should show system architecture, service responsibilities, and demo commands.

## Release version pattern

Use semantic versioning:

```text
v1.0.0  stable first portfolio release
v1.1.0  new feature release
v1.1.1  bug fix release
```

## GitHub CLI release command

Create a file called `RELEASE_NOTES.md` inside the target repository, then run:

```bash
gh release create v1.0.0 --title "v1.0.0 - Portfolio Release" --notes-file RELEASE_NOTES.md
```

## Release notes template

````markdown
# v1.0.0 - Portfolio Release

## Highlights

- Production-style backend/project structure
- Clear README with setup instructions
- Test command documented
- CI badge added
- Architecture diagram added

## Technical details

- Language/framework:
- Database/storage:
- Authentication/security:
- Deployment:
- Test coverage:

## How to run

```bash
# add project-specific commands here
```

## Known limitations

- Add honest limitations here.
````
