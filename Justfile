# Fetch GitHub repos metadata only
fetch-repos *args:
    python3 scripts/fetch-repos.py {{ args }}

# Fetch metadata and refresh only missing/stale LLM summaries
fetch-repos-summaries *args:
    python3 scripts/fetch-repos.py --refresh-summaries {{ args }}

# Fetch metadata and fully regenerate all LLM summaries
fetch-repos-summaries-force:
    python3 scripts/fetch-repos.py --refresh-summaries --force

# Build site (fetch + zola)
build: fetch-repos
    zola build

# Serve locally
serve:
    zola serve

# Deploy: build and push to master
deploy: build
    git add -A
    git commit -m "Update site"
    git push origin master
