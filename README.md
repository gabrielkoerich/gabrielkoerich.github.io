# gabrielkoerich.github.io

Personal projects and repositories website for Gabriel Koerich.

Live URL: https://gabrielkoerich.com/projects

## What It Is

This repository contains the source code for a static site that lists repositories, shows project summaries, and displays language usage across projects.

## What It Does

- Builds and publishes a projects page using Zola.
- Shows repository metadata such as stars, last update date, languages, and links.
- Uses a separate descriptions dataset for long-form repository summaries.
- Deploys to GitHub Pages on push and on a daily schedule.

## How It Works

1. `scripts/fetch-repos.py` fetches repository metadata from the GitHub API and writes `data/repos.json`.
2. LLM-generated summaries are stored separately in `data/repo-descriptions.json`.
3. `templates/index.html` loads both files and renders:
   - summary from `repo-descriptions.json` when available
   - GitHub description as fallback
4. Zola builds the static site from templates + data.
5. GitHub Actions (`.github/workflows/deploy.yml`) runs scheduled and push builds.

## Common Commands

- `just fetch-repos`: refresh metadata only (no LLM).
- `just fetch-repos-summaries`: refresh metadata and summaries.
- `just fetch-repos-summaries-force`: regenerate all summaries.
- `just build`: fetch metadata and build site.
- `just serve`: run local dev server.

## Notes

- The workflow uses `REPOS_TOKEN` to fetch owned repositories (including private repos metadata as needed for rendering).
- The default workflow fetch step does not call LLM.
