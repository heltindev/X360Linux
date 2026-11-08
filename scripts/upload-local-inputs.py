#!/usr/bin/env python3
"""Stage a locally compiled archive on GitHub for the lightweight packaging Action.
Windows Python + an existing Git Credential Manager login. No token is printed.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile
import urllib.error
import urllib.parse
import urllib.request

REPO = "heltindev/X360Linux"
CACHE_TAG = "x360linux-local-cache"

def api(url, token, method="GET", body=None, content_type="application/json"):
    headers = {
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json",
        "Content-Type": content_type,
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "X360Linux-local-builder",
    }
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            result = response.read()
            return json.loads(result) if result else None
    except urllib.error.HTTPError as err:
        raise RuntimeError(f"GitHub returned HTTP {err.code}: " +
                           err.read().decode("utf-8", "replace")[:300]) from err

def verify(archive):
    assert archive.is_file() and archive.stat().st_size > 1024
    with tarfile.open(archive, "r:gz") as tf:
        members = {Path(i.name).name: i for i in tf if i.isfile()}
        assert {"SOURCE_COMMIT.txt", "SHA256SUMS"}.issubset(members)
        commit = tf.extractfile(members["SOURCE_COMMIT.txt"]).read().decode().strip()
        assert len(commit) == 40 and all(c in "0123456789abcdef" for c in commit)
        assert archive.name == f"X360Linux-local-inputs-{commit[:8]}.tar.gz"
        checksum = tf.extractfile(members["SHA256SUMS"]).read().decode()
        assert "debian/debian-ports-powerpc-rootfs.tar.gz" in checksum
        assert "kernel/vmlinux" in checksum
        assert "recovery/initramfs.cpio.gz" in checksum
    with archive.open("rb") as handle:
        fingerprint = hashlib.file_digest(handle, "sha256").hexdigest()
    return commit, "sha256:" + fingerprint

def credentials():
    env = dict(os.environ, GCM_INTERACTIVE="never", GIT_TERMINAL_PROMPT="0")
    result = subprocess.run(["git", "credential", "fill"],
                            input="protocol=https\nhost=github.com\n\n",
                            capture_output=True, text=True, timeout=30, env=env,
                            check=True)
    details = dict(line.split("=", 1) for line in result.stdout.splitlines()
                   if "=" in line)
    if not details.get("password"):
        raise RuntimeError("GitHub login unavailable in Windows Git Credential Manager")
    return details["password"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("archive", type=Path)
    args = ap.parse_args()
    commit, digest = verify(args.archive)
    print(f"LOCAL_INPUT_VERIFIED commit={commit}, bytes={args.archive.stat().st_size}", flush=True)
    token = credentials()
    base = f"https://api.github.com/repos/{REPO}"
    try:
        release = api(base + "/releases/tags/" + CACHE_TAG, token)
    except RuntimeError as err:
        if "HTTP 404" not in str(err):
            raise
        release = api(base + "/releases", token, method="POST", body=json.dumps({
            "tag_name": CACHE_TAG, "target_commitish": "main",
            "name": "X360Linux local build cache (not a console release)",
            "body": "Cached PC-compiled inputs for the reproducible XeLL/ISO workflow.",
            "prerelease": True, "draft": False
        }).encode())
    assets = {a["name"]: a for a in release["assets"]}
    if args.archive.name in assets:
        old = assets[args.archive.name]
        if old.get("digest") != digest or old.get("size") != args.archive.stat().st_size:
            raise RuntimeError("An archive with this commit name already exists with different bytes.")
        print("LOCAL_INPUT_ALREADY_UPLOADED", args.archive.name)
        return
    url = f"https://uploads.github.com/repos/{REPO}/releases/{release['id']}/assets?"
    url += urllib.parse.urlencode({"name": args.archive.name})
    with args.archive.open("rb") as file:
        uploaded = api(url, token, method="POST", body=file.read(),
                       content_type="application/gzip")
    assert uploaded["state"] == "uploaded"
    assert uploaded["digest"] == digest
    print("STAGED_TO_GITHUB", uploaded["browser_download_url"], flush=True)
    print("Now run: GitHub Actions -> Package precompiled Linux with XeLL and ISO")

if __name__ == "__main__":
    main()
