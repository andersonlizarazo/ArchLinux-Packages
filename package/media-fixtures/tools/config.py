"""Paths and pinned external sources for the fixture toolchain."""

from pathlib import Path

# tools/config.py -> the media-fixtures project directory.
PROJECT_DIR = Path(__file__).resolve().parent.parent
FIXTURES_DIR = PROJECT_DIR / "fixtures"
CACHE_DIR = PROJECT_DIR / "cache"
SOURCES_DIR = PROJECT_DIR / "sources"
COMMONS_INDEX_PATH = SOURCES_DIR / "commons.json"
MANIFEST_PATH = PROJECT_DIR / "manifest.json"
EXPECTED_PATH = PROJECT_DIR / "EXPECTED.md"
TRANSCRIPTS_PATH = PROJECT_DIR / "TRANSCRIPTS.md"
ATTRIBUTION_PATH = PROJECT_DIR / "ATTRIBUTION.md"
CHECKSUMS_PATH = PROJECT_DIR / "checksums.txt"

SCHEMA_VERSION = 1
PKGVER = "1.0.0"

# Wikimedia throttles bulk download that lacks a descriptive user agent.
USER_AGENT = (
    "media-fixtures/1.0 (Arch Linux test-fixture package; "
    "+https://wiki.archlinux.org/title/Arch_package_guidelines)"
)

# Originals above this size are downloaded as a resized thumbnail instead.
ORIGINAL_BYTES_MAX = 8 * 1024 * 1024
THUMBNAIL_WIDTH_MAX = 1600

# Durations measured through re-encoding drift by a few milliseconds.
DURATION_TOLERANCE_S = 0.06
