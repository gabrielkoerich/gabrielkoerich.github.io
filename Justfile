# Default recipe - show available commands
default:
    @just --list

# Fetch GitHub repos metadata only
fetch-repos *args:
    python3 scripts/fetch-repos.py {{ args }}

# Fetch metadata and refresh only missing/stale LLM summaries
fetch-repos-summaries *args:
    python3 scripts/fetch-repos.py --refresh-summaries {{ args }}

# Install the zola-docs theme, CI does the same through zola-docs-action
theme:
    #!/usr/bin/env bash
    set -euo pipefail
    src="$HOME/Projects/zola-docs-action/theme"
    if [ ! -d "$src" ]; then
        tmp=$(mktemp -d)
        git clone -q --depth 1 https://github.com/gabrielkoerich/zola-docs-action "$tmp"
        src="$tmp/theme"
    fi
    mkdir -p themes
    [ -d themes/zola-docs ] && trash themes/zola-docs
    cp -R "$src" themes/zola-docs

# Build site (fetch + zola)
build: fetch-repos theme
    zola build

# Serve locally
serve: theme
    zola serve

# Serve with live-reload and open browser
watch: theme
    zola serve --open

alias dev := watch

# Deploy: build and push to master
deploy: build
    git add -A
    git commit -m "Update site"
    git push origin master
