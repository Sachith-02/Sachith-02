# Security Policy

This repository contains profile automation scripts and GitHub Actions workflows.

## Reporting

Please open a private security advisory or contact the repository owner if you find an issue related to automation scripts, workflow permissions, or token handling.

## Automation security standards

- Workflows use the smallest practical permissions.
- The README update workflow uses `contents: write` only where commits are required.
- Public GitHub data is used for profile generation.
- Secrets should never be printed in workflow logs.
