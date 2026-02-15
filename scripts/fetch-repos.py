#!/usr/bin/env python3
"""Fetch all GitHub repos (public + private) and extract README summaries."""

import json
import os
import re
import subprocess
import sys
import base64
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError


# GitHub language colors (common ones)
LANG_COLORS = {
    "Rust": "#dea584",
    "Python": "#3572A5",
    "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6",
    "PHP": "#4F5D95",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "SCSS": "#c6538c",
    "Shell": "#89e051",
    "Go": "#00ADD8",
    "Ruby": "#701516",
    "Java": "#b07219",
    "C": "#555555",
    "C++": "#f34b7d",
    "C#": "#178600",
    "Swift": "#F05138",
    "Kotlin": "#A97BFF",
    "Dart": "#00B4AB",
    "Vue": "#41b883",
    "Svelte": "#ff3e00",
    "Solidity": "#AA6746",
    "Makefile": "#427819",
    "Dockerfile": "#384d54",
    "Lua": "#000080",
    "Vim Script": "#199f4b",
    "Nix": "#7e7eff",
    "Zig": "#ec915c",
    "Haskell": "#5e5086",
    "Elixir": "#6e4a7e",
    "Blade": "#f7523f",
    "Jupyter Notebook": "#DA5B0B",
}


def get_token():
    """Get GitHub token from gh CLI or environment."""
    try:
        result = subprocess.run(
            ["gh", "auth", "token"], capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        return token

    print("Error: No GitHub token found. Run 'gh auth login' or set GITHUB_TOKEN.", file=sys.stderr)
    sys.exit(1)


def api_get(url, token):
    """Make authenticated GitHub API request."""
    req = Request(url)
    req.add_header("Authorization", f"token {token}")
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("User-Agent", "fetch-repos-script")
    try:
        with urlopen(req) as resp:
            return json.loads(resp.read()), resp.headers
    except HTTPError as e:
        if e.code == 404:
            return None, {}
        raise


def fetch_all_repos(token):
    """Fetch all repos with pagination."""
    repos = []
    url = "https://api.github.com/user/repos?per_page=100&sort=updated&affiliation=owner"

    while url:
        data, headers = api_get(url, token)
        repos.extend(data)

        # Parse Link header for next page
        link = headers.get("Link", "")
        url = None
        for part in link.split(","):
            if 'rel="next"' in part:
                url = part.split("<")[1].split(">")[0]

    return repos


def fetch_pages_url(token, owner, repo_name):
    """Fetch GitHub Pages URL if enabled."""
    url = f"https://api.github.com/repos/{owner}/{repo_name}/pages"
    data, _ = api_get(url, token)
    if data and data.get("html_url"):
        return data["html_url"]
    return None


def fetch_languages(token, owner, repo_name):
    """Fetch repo languages sorted by bytes descending. Returns (display list, raw dict)."""
    url = f"https://api.github.com/repos/{owner}/{repo_name}/languages"
    data, _ = api_get(url, token)
    if not data:
        return [], {}
    total = sum(data.values())
    if total == 0:
        return [], {}
    display = [
        {"name": lang, "color": LANG_COLORS.get(lang, "#58a6ff")}
        for lang, _ in sorted(data.items(), key=lambda x: x[1], reverse=True)
    ]
    return display, data


def fetch_readme(token, owner, repo_name):
    """Fetch raw README content."""
    url = f"https://api.github.com/repos/{owner}/{repo_name}/readme"
    data, _ = api_get(url, token)

    if not data or "content" not in data:
        return None

    try:
        return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
    except Exception:
        return None


def summarize_with_claude(repo_name, description, readme_content):
    """Use claude -p to generate a one-line project summary."""
    # Truncate README to avoid huge inputs
    readme_truncated = readme_content[:3000] if readme_content else ""

    prompt = (
        f"You have all the information you need below. Do NOT ask for more info.\n\n"
        f"Project name: {repo_name}\n"
        f"Description: {description or 'none'}\n"
        f"README content:\n{readme_truncated}\n\n"
        f"Using ONLY the information above, write a 2-3 sentence summary of this project. "
        f"Start directly with a noun or verb (e.g. 'A tool that...' or 'CLI for...'). "
        f"NEVER ask questions. NEVER say you need more info. NEVER use preamble. "
        f"Output ONLY the summary text. No markdown. No quotes."
    )

    try:
        env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
        result = subprocess.run(
            ["claude", "-p", "--model", "haiku", prompt],
            capture_output=True, text=True, timeout=30, env=env, cwd="/tmp",
        )
        if result.returncode == 0:
            summary = result.stdout.strip()
            summary = summary.strip('"\'')
            # Strip LLM preamble if present
            # Strip any LLM preamble
            summary = re.sub(
                r"^(Based on[^,:.]*[,:.]?\s*|Here'?s?\s[^,:]*[,:]\s*|I'd be happy[^.]*\.\s*|Sure[,!.]\s*|The README mentions[^.]*\.\s*)",
                "", summary, count=1, flags=re.IGNORECASE
            ).lstrip(" .,:-\n")
            # Strip "summary:" prefix if present
            if re.match(r"^.*?summary[:\s]", summary[:60], re.IGNORECASE):
                summary = re.sub(r"^.*?summary[:\s]+", "", summary, count=1, flags=re.IGNORECASE)
            # Reject if LLM refused, asked for access, or gave a vague answer
            reject = re.search(
                r"(I don't have|I need access|Could you|I cannot|I can't|provide me|access to the repo|clarify which|Do you have|Once I have|I'll need|you want summarized|Can you provide|I see this is|not documented|appears to be|though specific|functionality details|no available description|no available README|without documented|no description or README|not enough information)",
                summary, re.IGNORECASE
            )
            if reject:
                return None
            return summary
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return None


def load_cache(out_path):
    """Load existing summaries as a cache keyed by repo name."""
    if not out_path.exists():
        return {}
    try:
        data = json.loads(out_path.read_text())
        return {r["name"]: r.get("summary", "") for r in data.get("repos", [])}
    except (json.JSONDecodeError, KeyError):
        return {}


BLACKLIST = {
    "oblivion",
    "nasc",
    "iter-landing-page",
    "acupunturafloripa",
    "algorit-wp-theme",
    "bulldesk-cf7-integration",
    "bulldesk-site",
    "iter",
    "tracelog",
    "medical",
    "momentodohler",
    "formabella",
    "three",
    "koerich-consultoria",
    "fundamentando",
    "testing",
    "projects",
    "report",
    "partners",
    "iafut-backend",
    "cross-domain",
}


def main():
    force = "--force" in sys.argv

    token = get_token()
    out_path = Path(__file__).parent.parent / "data" / "repos.json"
    cache = {} if force else load_cache(out_path)

    print("Fetching repos...", file=sys.stderr)
    repos = fetch_all_repos(token)
    # Filter out forks and blacklisted repos
    repos = [r for r in repos if not r.get("fork") and r["name"] not in BLACKLIST]
    print(f"Found {len(repos)} repos", file=sys.stderr)

    results = []
    all_lang_bytes = {}
    skipped = 0
    for i, repo in enumerate(repos):
        owner = repo["owner"]["login"]
        name = repo["name"]
        description = repo.get("description") or ""

        cached_summary = cache.get(name, "")
        if cached_summary:
            summary = cached_summary
            skipped += 1
            print(f"  [{i+1}/{len(repos)}] {name} (cached)", file=sys.stderr)
        else:
            print(f"  [{i+1}/{len(repos)}] {name}", file=sys.stderr)
            homepage = repo.get("homepage") or ""
            readme = fetch_readme(token, owner, name)
            readme_is_thin = not readme or len(readme.strip()) < 20

            if readme_is_thin and homepage:
                summary = f"Website code for {homepage}."
                print(f"    -> website fallback ({homepage})", file=sys.stderr)
            elif not readme:
                if description:
                    summary = ""
                    print(f"    -> no README, using description", file=sys.stderr)
                else:
                    print(f"    -> skipped (no README or description)", file=sys.stderr)
                    continue
            else:
                summary = summarize_with_claude(name, description, readme) or ""

        languages, lang_bytes = fetch_languages(token, owner, name)
        pages_url = fetch_pages_url(token, owner, name)

        # Fallback for repos with no useful summary
        if not summary and (repo.get("homepage") or ""):
            summary = f"Website code for {repo['homepage']}."
        elif not summary and pages_url:
            summary = f"Website code for {pages_url}."
        # Weight adjustments and exclusions for aggregate chart
        LANG_HIDE = {"HTML", "CSS"}
        LANG_WEIGHT = {"Jupyter Notebook": 0.1, "Rust": 2}
        for lang, bytes_count in lang_bytes.items():
            if lang in LANG_HIDE:
                continue
            weight = LANG_WEIGHT.get(lang, 1)
            all_lang_bytes[lang] = all_lang_bytes.get(lang, 0) + int(bytes_count * weight)

        results.append({
            "name": name,
            "description": description,
            "summary": summary,
            "html_url": repo["html_url"],
            "private": repo["private"],
            "languages": languages,
            "pages_url": pages_url or "",
            "stargazers_count": repo.get("stargazers_count", 0),
            "topics": repo.get("topics", []),
            "created_at": repo["created_at"],
            "updated_at": repo["updated_at"],
            "archived": repo.get("archived", False),
            "fork": repo.get("fork", False),
        })

    # Sort by creation year (descending), then stars within each year (descending)
    results.sort(key=lambda r: r["stargazers_count"], reverse=True)
    results.sort(key=lambda r: int(r["created_at"][:4]), reverse=True)

    # Aggregate language breakdown
    total_bytes = sum(all_lang_bytes.values()) or 1
    lang_sorted = sorted(all_lang_bytes.items(), key=lambda x: x[1], reverse=True)
    lang_breakdown = []
    other_pct = 0
    for lang, bytes_count in lang_sorted:
        pct = round(bytes_count / total_bytes * 100, 1)
        if pct >= 0.5:
            lang_breakdown.append({
                "name": lang,
                "color": LANG_COLORS.get(lang, "#58a6ff"),
                "percentage": pct,
            })
        else:
            other_pct += pct

    if other_pct > 0:
        lang_breakdown.append({
            "name": "Other",
            "color": "#8b949e",
            "percentage": round(other_pct, 1),
        })

    output = {"languages": lang_breakdown, "repos": results}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2))

    print(f"Wrote {len(results)} repos ({skipped} cached) to {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
