# Default recipe - show available commands
default:
    @just --list

# Fetch GitHub repos metadata only
fetch-repos *args:
    python3 scripts/fetch-repos.py {{ args }}

# Fetch metadata and refresh only missing/stale LLM summaries
fetch-repos-summaries *args:
    python3 scripts/fetch-repos.py --refresh-summaries {{ args }}

# Build site (fetch + zola)
build: fetch-repos
    zola build

# Serve locally
serve:
    zola serve

# Serve with live-reload and open browser
watch:
    zola serve --open

alias dev := watch

# Deploy: build and push to master
deploy: build
    git add -A
    git commit -m "Update site"
    git push origin master
