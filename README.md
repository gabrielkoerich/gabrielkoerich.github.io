# [gabrielkoerich.github.io](https://gabrielkoerich.com/projects)

A self-updating portfolio that pulls my GitHub repos, generates project summaries with Claude, and publishes a clean static site — rebuilt daily.

## How it works

A Python script queries the GitHub API for every repo I own, fetches language stats, and optionally sends each README through Claude (Haiku) to produce concise two-sentence descriptions. The output lands in two JSON files — one for repo metadata, one for summaries — which Zola picks up at build time to render a single-page site grouped by year, complete with an aggregate language bar, star counts, and direct links.

GitHub Actions runs the full pipeline on every push and once a day on a cron schedule.

```
scripts/fetch-repos.py  →  data/repos.json
                            data/repo-descriptions.json
templates/index.html     →  reads both JSON files
zola build               →  static site in public/
```

## Development

```sh
just serve          # local dev server with live reload
just build          # fetch repos + build site
just fetch-repos    # refresh repo metadata only
```

To regenerate LLM summaries:

```sh
just fetch-repos-summaries        # refresh missing/stale summaries
just fetch-repos-summaries-force  # regenerate all from scratch
```

## Stack

[Zola](https://www.getzola.org) for static site generation, plain HTML/CSS templates, Python for data fetching, and GitHub Actions for CI/CD. No JavaScript frameworks. Summaries powered by [Claude](https://claude.ai) via the `claude` CLI.
