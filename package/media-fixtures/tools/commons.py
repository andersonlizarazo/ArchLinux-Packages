"""Pinned Wikimedia Commons downloads and their attribution records."""

import json
import re
import urllib.parse
import urllib.request
from html import unescape
from pathlib import Path

import config
import media

API_URL = "https://commons.wikimedia.org/w/api.php"
REQUEST_TIMEOUT_S = 120
DOWNLOAD_CHUNK_BYTES = 1 << 16
TAG_PATTERN = re.compile(r"<[^>]+>")
SPACE_PATTERN = re.compile(r"\s+")
LICENSE_PREFIXES = ("Public domain", "CC0", "PD")


def plain_text(value):
    """Strip HTML and collapse whitespace in a Commons metadata field."""
    without_tags = TAG_PATTERN.sub(" ", value or "")
    text = SPACE_PATTERN.sub(" ", unescape(without_tags)).strip()
    assert "<" not in text, "plain_text: leftover tag"
    return text


def api_query(parameters):
    """Run one read-only Commons API query."""
    query = dict(parameters, format="json", formatversion="2")
    url = f"{API_URL}?{urllib.parse.urlencode(query)}"
    assert url.startswith("https://commons.wikimedia.org/"), "api_query: url"
    request = urllib.request.Request(
        url, headers={"User-Agent": config.USER_AGENT}
    )
    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_S) as response:
        payload = json.load(response)
    assert isinstance(payload, dict), "api_query: payload type"
    return payload


def fetch_record(title):
    """Fetch the download and attribution record for one Commons file."""
    assert title.startswith("File:"), f"fetch_record: bad title {title}"
    payload = api_query(
        {
            "action": "query",
            "titles": title,
            "prop": "imageinfo",
            "iiprop": "url|size|mime|extmetadata",
            "iiurlwidth": str(config.THUMBNAIL_WIDTH_MAX),
        }
    )
    pages = payload.get("query", {}).get("pages", [])
    assert len(pages) == 1, f"fetch_record: pages {len(pages)} for {title}"
    info = (pages[0].get("imageinfo") or [{}])[0]
    assert info.get("url"), f"fetch_record: no url for {title}"
    metadata = info.get("extmetadata", {})
    record = {
        "title": title,
        "original_url": info["url"],
        "thumbnail_url": info.get("thumburl", ""),
        "description_url": info.get("descriptionurl", ""),
        "original_bytes": int(info.get("size", 0)),
        "original_width": int(info.get("width", 0)),
        "original_height": int(info.get("height", 0)),
        "mime": info.get("mime", ""),
        "description": plain_text(
            metadata.get("ImageDescription", {}).get("value")
        ),
        "author": plain_text(metadata.get("Artist", {}).get("value")),
        "license": plain_text(
            metadata.get("LicenseShortName", {}).get("value")
        ),
        "license_url": metadata.get("LicenseUrl", {}).get("value", ""),
        "date": plain_text(metadata.get("DateTimeOriginal", {}).get("value")),
    }
    if not record["license"].startswith(LICENSE_PREFIXES):
        raise media.MediaError(
            f"{title}: not a public domain file ({record['license']})"
        )
    assert record["original_bytes"] > 0, f"fetch_record: zero size {title}"
    return record


def load_index():
    """Return the committed source index, empty when absent."""
    if not config.COMMONS_INDEX_PATH.is_file():
        return {}
    with config.COMMONS_INDEX_PATH.open(encoding="utf-8") as handle:
        index = json.load(handle)
    assert isinstance(index, dict), "load_index: index type"
    return index


def save_index(index):
    """Write the source index with sorted keys."""
    assert index, "save_index: empty index"
    config.SOURCES_DIR.mkdir(parents=True, exist_ok=True)
    ordered = {title: index[title] for title in sorted(index)}
    with config.COMMONS_INDEX_PATH.open("w", encoding="utf-8") as handle:
        json.dump(ordered, handle, indent=2, sort_keys=True)
        handle.write("\n")


def ensure_index(titles, refresh=False):
    """Fetch metadata for every title that is missing or being refreshed."""
    assert titles, "ensure_index: no titles"
    index = load_index()
    for title in sorted(set(titles)):
        if refresh or title not in index:
            index[title] = fetch_record(title)
    if set(titles) - set(index):
        raise media.MediaError("ensure_index: unresolved titles")
    assert all(title.startswith("File:") for title in index), (
        "ensure_index: keys"
    )
    return index


def download_url(record):
    """Pick the original, or a thumbnail under the size cap."""
    oversized = record["original_bytes"] > config.ORIGINAL_BYTES_MAX
    if oversized and record["mime"].startswith("image/"):
        return record["thumbnail_url"] or record["original_url"]
    return record["original_url"]


def cache_path(url):
    """Map a download URL to a stable cache file name."""
    name = urllib.parse.unquote(Path(urllib.parse.urlparse(url).path).name)
    assert name and "/" not in name, f"cache_path: bad name {name}"
    return config.CACHE_DIR / name


def download(url, target):
    """Download `url` to `target` through a temporary file."""
    assert url.startswith("https://"), f"download: url scheme {url}"
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".part")
    request = urllib.request.Request(
        url, headers={"User-Agent": config.USER_AGENT}
    )
    with (
        urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_S) as response,
        temporary.open("wb") as handle,
    ):
        while True:
            chunk = response.read(DOWNLOAD_CHUNK_BYTES)
            if not chunk:
                break
            handle.write(chunk)
    if temporary.stat().st_size == 0:
        raise media.MediaError(f"download: empty body {url}")
    assert temporary.is_file(), "download: temporary missing"
    temporary.replace(target)
    return target


def ensure_source(index, recipe):
    """Return the cached source file for a commons recipe."""
    assert recipe.source_title in index, (
        f"ensure_source: unpinned {recipe.name}"
    )
    record = index[recipe.source_title]
    url = download_url(record)
    if record.get("download_url") not in (None, url):
        for key in ("download_url", "download_sha256", "download_bytes"):
            record.pop(key, None)
    target = cache_path(url)
    pinned = record.get("download_sha256")
    if target.is_file() and pinned:
        if media.sha256_file(target) == pinned:
            return target
    target.unlink(missing_ok=True)
    download(url, target)
    actual_bytes = target.stat().st_size
    if url == record["original_url"]:
        if actual_bytes != record["original_bytes"]:
            raise media.MediaError(
                f"{recipe.name}: truncated download, {actual_bytes} bytes"
            )
    digest = media.sha256_file(target)
    if pinned:
        if digest != pinned:
            raise media.MediaError(f"{recipe.name}: source checksum changed")
    else:
        record["download_url"] = url
        record["download_sha256"] = digest
        record["download_bytes"] = actual_bytes
    assert record["download_sha256"] == digest, "ensure_source: pin mismatch"
    return target
