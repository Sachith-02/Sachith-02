# Contributing

This is a personal GitHub profile automation repository. Contributions should keep the README clean, professional, and easy to maintain.

## Quality checklist

- Run `python -m unittest discover -s tests -v`
- Run `python .github/scripts/readme_lint.py`
- Run `python .github/scripts/profile_health_check.py --check-only`
- Keep dynamic README blocks inside their marker pairs
- Update `profile.config.json` when adding new workflows or sections
