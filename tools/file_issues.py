#!/usr/bin/env python3
"""File the ready-to-file GitHub issues in docs/issues/*.yml.

The v3.0 revival's automation token was read-only, so the first wave of issues
is checked into docs/issues/ instead of the tracker. Run this once a token with
`issues:write` is available to create them for real.

Usage:
    GITHUB_TOKEN=ghp_xxx python3 tools/file_issues.py docs/issues/v3.0-sprint-01.yml

Idempotent: skips any issue whose exact title already exists (open or closed),
so re-running after granting access is safe.

Stdlib only (yaml is the single external dep, already required by the engine).
"""
import json
import os
import sys
import urllib.request

import yaml

API = "https://api.github.com"


def _req(method, url, token, data=None):
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "mojobol-file-issues")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def existing_titles(owner, repo, token):
    titles, page = set(), 1
    while True:
        batch = _req(
            "GET",
            f"{API}/repos/{owner}/{repo}/issues?state=all&per_page=100&page={page}",
            token,
        )
        if not batch:
            break
        titles.update(i["title"] for i in batch if "pull_request" not in i)
        page += 1
    return titles


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: file_issues.py <issues.yml>")
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("error: set GITHUB_TOKEN (needs issues:write)")

    spec = yaml.safe_load(open(sys.argv[1]))
    owner, repo = spec["repo"].split("/")
    default_labels = spec.get("default_labels", [])

    have = existing_titles(owner, repo, token)
    created = skipped = 0
    for issue in spec["issues"]:
        if issue["title"] in have:
            print(f"skip (exists): {issue['title']}")
            skipped += 1
            continue
        payload = {
            "title": issue["title"],
            "body": issue["body"],
            "labels": issue.get("labels", default_labels),
        }
        result = _req(
            "POST", f"{API}/repos/{owner}/{repo}/issues", token, payload
        )
        print(f"created #{result['number']}: {issue['title']}")
        created += 1
    print(f"\ndone: {created} created, {skipped} skipped")


if __name__ == "__main__":
    main()
