# Fetch GitHub repos data (use --force to regenerate all summaries)
fetch-repos *args:
    python3 scripts/fetch-repos.py {{ args }}

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
