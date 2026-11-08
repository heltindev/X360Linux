#!/usr/bin/env bash
# Publish validated ZIP archives; keep the release tag fixed as a rolling alpha.
set -euo pipefail
directory="${1:-dist/publish}"
tag="v0.3.0-alpha"
repo="${GITHUB_REPOSITORY:-heltindev/X360Linux}"
: "${GH_TOKEN:?GitHub Actions token with contents:write required}"

python3 release/verify_usb_release.py "$directory" --tag "$tag"
gh release view "$tag" --repo "$repo" >/dev/null
gh release upload "$tag" \
    "$directory/X360Linux-$tag-RGH-USB.zip" \
    "$directory/X360Linux-$tag-ABadAvatar-FreeMyXe-USB.zip" \
    "$directory/SHA256SUMS" \
    --repo "$repo" --clobber

notes_file="$(mktemp)"
trap 'rm -f "$notes_file"' EXIT
cat release/v03-release-notes.md > "$notes_file"
printf '\n---\nVerified build source commit: `%s`.\n' "${SOURCE_SHA:-unknown}" >> "$notes_file"
gh release edit "$tag" --repo "$repo" --prerelease --notes-file "$notes_file"
echo "PUBLISHED_READY_TO_COPY_RELEASE=https://github.com/$repo/releases/tag/$tag"
