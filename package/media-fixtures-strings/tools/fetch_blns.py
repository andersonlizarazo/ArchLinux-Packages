"""Fetch the pinned Big List of Naughty Strings release.

Upstream publishes no tagged releases, so the commit is pinned in
`upstream.json`. Running this again re-downloads the pinned commit and fails
when the content or a checksum changed.
"""

import hashlib
import json
import urllib.request
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
UPSTREAM_PATH = PROJECT_DIR / "upstream.json"
REPOSITORY = "minimaxir/big-list-of-naughty-strings"
FILES = ("blns.txt", "blns.json", "LICENSE")
RAW_URL = "https://raw.githubusercontent.com/{repo}/{commit}/{name}"
COMMITS_URL = f"https://api.github.com/repos/{REPOSITORY}/commits/master"
USER_AGENT = "media-fixtures-strings/1.0 (Arch Linux fixture package)"
REQUEST_TIMEOUT_S = 60
MIT_BODY = "Permission is hereby granted, free of charge"


class FetchError(RuntimeError):
    """Upstream content is missing or no longer matches the pinned checksums."""


def request(url):
    """Fetch a URL and return the raw bytes."""
    assert url.startswith("https://"), f"request: url scheme {url}"
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/vnd.github+json",
    }
    with urllib.request.urlopen(
        urllib.request.Request(url, headers=headers), timeout=REQUEST_TIMEOUT_S
    ) as response:
        data = response.read()
    assert data, f"request: empty body {url}"
    return data


def digest(data):
    """Return the hex SHA-256 of a byte string."""
    assert data, "digest: empty data"
    text = hashlib.sha256(data).hexdigest()
    assert len(text) == 64, "digest: width"
    return text


def load_pin():
    """Return the committed pin, or an empty dict when absent."""
    if not UPSTREAM_PATH.is_file():
        return {}
    with UPSTREAM_PATH.open(encoding="utf-8") as handle:
        pin = json.load(handle)
    assert pin["commit"], "load_pin: no commit"
    return pin


def resolve_commit():
    """Ask GitHub for the current commit of the default branch."""
    payload = json.loads(request(COMMITS_URL))
    commit = payload["sha"]
    assert len(commit) == 40, f"resolve_commit: odd sha {commit}"
    return commit, payload["commit"]["committer"]["date"]


def fetch_files(commit):
    """Download every pinned file through the raw content endpoint."""
    assert len(commit) == 40, "fetch_files: commit"
    downloaded = {}
    for name in FILES:
        url = RAW_URL.format(repo=REPOSITORY, commit=commit, name=name)
        downloaded[name] = request(url)
        assert downloaded[name], f"fetch_files: empty {name}"
    return downloaded


def assert_pinned(pin, downloaded):
    """Assert every downloaded file matches the committed pin."""
    for name, data in downloaded.items():
        if digest(data) != pin["files"][name]["sha256"]:
            raise FetchError(f"{name}: checksum differs from upstream.json")
    assert MIT_BODY.encode() in downloaded["LICENSE"], "assert_pinned: not MIT"


def build_pin(commit, committed_at, downloaded):
    """Build the pin record for a freshly resolved commit."""
    assert MIT_BODY.encode() in downloaded["LICENSE"], "build_pin: not MIT"
    strings = json.loads(downloaded["blns.json"])
    assert isinstance(strings, list), "build_pin: blns.json shape"
    assert len(strings) > 500, f"build_pin: only {len(strings)} strings"
    return {
        "repository": REPOSITORY,
        "commit": commit,
        "committed_at": committed_at,
        "license": "MIT",
        "files": {
            name: {"sha256": digest(data), "bytes": len(data)}
            for name, data in sorted(downloaded.items())
        },
    }


def write_files(downloaded):
    """Write the downloaded files into the package directory."""
    written = []
    for name, data in sorted(downloaded.items()):
        target = PROJECT_DIR / name
        target.write_bytes(data)
        assert target.stat().st_size == len(data), f"write_files: short {name}"
        written.append(target)
    return written


def main():
    pin = load_pin()
    if pin:
        commit = pin["commit"]
        committed_at = pin.get("committed_at", "")
    else:
        commit, committed_at = resolve_commit()
    downloaded = fetch_files(commit)
    if pin:
        assert_pinned(pin, downloaded)
    else:
        pin = build_pin(commit, committed_at, downloaded)
        UPSTREAM_PATH.write_text(
            json.dumps(pin, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    written = write_files(downloaded)
    for path in written:
        print(f"{path.name}: {path.stat().st_size} bytes")
    print(f"commit {commit}")


if __name__ == "__main__":
    main()
