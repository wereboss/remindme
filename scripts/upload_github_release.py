#!/usr/bin/env python3
"""
Uploads distribution packages to GitHub Releases for wereboss/remindme
Uses GitHub REST API (zero extra dependencies, pure standard library urllib).
"""

import os
import sys
import json
import mimetypes
import urllib.request
import urllib.error

REPO = "wereboss/remindme"
TAG = "v0.3.0"
RELEASE_TITLE = "v0.3.0 — Notes & Reminders PWA"

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST_DIR = os.path.join(PROJECT_ROOT, "dist")
NOTES_FILE = os.path.join(PROJECT_ROOT, "RELEASE_NOTES.md")

def get_token():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token and len(sys.argv) > 1:
        token = sys.argv[1].strip()
    return token

def get_release_notes():
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return f"Release {TAG} for {REPO}."

def api_request(url, method="GET", data=None, headers=None):
    if headers is None:
        headers = {}
    if data is not None and isinstance(data, (dict, list)):
        data = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    return urllib.request.urlopen(req)

def get_or_create_release(token, notes):
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "RemindMe-Uploader",
    }

    # Check existing releases
    list_url = f"https://api.github.com/repos/{REPO}/releases"
    try:
        with api_request(list_url, headers=headers) as resp:
            releases = json.loads(resp.read().decode("utf-8"))
            for rel in releases:
                if rel.get("tag_name") == TAG:
                    print(f"[*] Found existing release for tag {TAG} (ID: {rel['id']})")
                    return rel
    except urllib.error.HTTPError as e:
        print(f"[-] Error querying releases: {e.code} {e.reason}")
        print(e.read().decode("utf-8"))
        sys.exit(1)

    # Create new release
    print(f"[*] Creating GitHub Release '{RELEASE_TITLE}' for tag {TAG}...")
    create_url = f"https://api.github.com/repos/{REPO}/releases"
    payload = {
        "tag_name": TAG,
        "target_commitish": "main",
        "name": RELEASE_TITLE,
        "body": notes,
        "draft": False,
        "prerelease": False,
    }

    try:
        with api_request(create_url, method="POST", data=payload, headers=headers) as resp:
            release = json.loads(resp.read().decode("utf-8"))
            print(f"[+] Created release successfully: {release['html_url']}")
            return release
    except urllib.error.HTTPError as e:
        print(f"[-] Error creating release: {e.code} {e.reason}")
        print(e.read().decode("utf-8"))
        sys.exit(1)

def upload_assets(token, release):
    upload_url_template = release["upload_url"].split("{")[0]
    headers_base = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "RemindMe-Uploader",
    }

    # Check already uploaded assets to avoid duplicate errors
    existing_asset_names = {a["name"]: a["id"] for a in release.get("assets", [])}

    if not os.path.exists(DIST_DIR):
        print(f"[-] dist directory does not exist: {DIST_DIR}")
        return

    for fname in sorted(os.listdir(DIST_DIR)):
        if fname.startswith("."):
            continue
        fpath = os.path.join(DIST_DIR, fname)
        if not os.path.isfile(fpath):
            continue

        if fname in existing_asset_names:
            print(f"[*] Asset '{fname}' is already uploaded. Skipping.")
            continue

        size_kb = os.path.getsize(fpath) / 1024
        print(f"[*] Uploading '{fname}' ({size_kb:.1f} KB)...")

        content_type = mimetypes.guess_type(fname)[0] or "application/octet-stream"
        with open(fpath, "rb") as f:
            file_bytes = f.read()

        upload_url = f"{upload_url_template}?name={fname}"
        upload_headers = dict(headers_base)
        upload_headers["Content-Type"] = content_type

        try:
            with api_request(upload_url, method="POST", data=file_bytes, headers=upload_headers) as resp:
                asset_info = json.loads(resp.read().decode("utf-8"))
                print(f"[+] Uploaded '{fname}': {asset_info['browser_download_url']}")
        except urllib.error.HTTPError as e:
            print(f"[-] Failed to upload '{fname}': {e.code} {e.reason}")
            print(e.read().decode("utf-8"))

def main():
    token = get_token()
    if not token:
        print("=" * 70)
        print(" GITHUB TOKEN REQUIRED FOR API UPLOAD")
        print("=" * 70)
        print("Please provide a GitHub Personal Access Token (PAT) with repo scope:")
        print("  1. Environment variable:")
        print("     export GITHUB_TOKEN=ghp_yourTokenHere")
        print("     python3 scripts/upload_github_release.py")
        print("\n  2. Or pass as an argument:")
        print("     python3 scripts/upload_github_release.py ghp_yourTokenHere")
        print("\n  3. Alternatively, if you have 'gh' CLI installed on your machine:")
        print(f"     gh release create {TAG} dist/* --title \"{RELEASE_TITLE}\" --notes-file RELEASE_NOTES.md")
        print("=" * 70)
        sys.exit(1)

    notes = get_release_notes()
    release = get_or_create_release(token, notes)
    upload_assets(token, release)
    print("\n[+] All release assets successfully published to GitHub!")
    print(f"[+] View release at: {release['html_url']}")

if __name__ == "__main__":
    main()
