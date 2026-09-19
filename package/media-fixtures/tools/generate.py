"""Generate, list and verify the media fixture set.

Generating writes `fixtures/`, `manifest.json`, `checksums.txt`,
`EXPECTED.md` and `ATTRIBUTION.md`. Verification re-measures every shipped
file and fails on any difference, so the documentation cannot drift.
"""

import argparse
import shutil
import sys

import commons
import config
import media
import recipes
import report

PROBES = {
    "image": media.probe_image,
    "animation": media.probe_animation,
    "audio": media.probe_media,
    "video": media.probe_media,
    "text": media.probe_text,
}


class FixtureError(RuntimeError):
    """A fixture is missing, damaged, or contradicts its declaration."""


def select(prefixes):
    """Return the recipes matching any of the given name prefixes."""
    assert prefixes is not None, "select: prefixes"
    if not prefixes:
        return list(recipes.RECIPES)
    chosen = [
        recipe
        for recipe in recipes.RECIPES
        if any(recipe.name.startswith(prefix) for prefix in prefixes)
    ]
    if not chosen:
        raise FixtureError(f"no recipe matches {prefixes}")
    return chosen


def probe(recipe):
    """Measure one fixture from disk."""
    if recipe.kind not in PROBES:
        raise FixtureError(f"{recipe.name}: unknown kind {recipe.kind}")
    return PROBES[recipe.kind](config.FIXTURES_DIR / recipe.name)


def assert_matches(recipe, measured):
    """Assert a measurement satisfies the recipe's declared values."""
    assert measured, f"{recipe.name}: empty measurement"
    assert recipe.expected, f"{recipe.name}: no declared expectations"
    for key, declared in recipe.expected.items():
        if key.endswith("_max") or key.endswith("_min"):
            base = key.rsplit("_", 1)[0]
            actual = measured.get(base)
            if actual is None:
                raise FixtureError(f"{recipe.name}: no measured {base}")
            if key.endswith("_max"):
                if actual > declared:
                    raise FixtureError(
                        f"{recipe.name}: {base} {actual} > {declared}"
                    )
            elif actual < declared:
                raise FixtureError(
                    f"{recipe.name}: {base} {actual} < {declared}"
                )
            continue
        if key not in measured:
            raise FixtureError(f"{recipe.name}: probe has no {key}")
        actual = measured[key]
        if key.endswith("_s"):
            drift = abs(float(actual) - float(declared))
            if drift > config.DURATION_TOLERANCE_S:
                raise FixtureError(
                    f"{recipe.name}: {key} {actual} != {declared}"
                )
        elif actual != declared:
            raise FixtureError(
                f"{recipe.name}: {key} is {actual!r}, declared {declared!r}"
            )


def build_record(recipe, measured, index):
    """Build the manifest record for one fixture."""
    path = config.FIXTURES_DIR / recipe.name
    record = {
        "path": recipe.name,
        "kind": recipe.kind,
        "origin": "commons" if recipe.source_title else "generated",
        "description": recipe.description,
        "properties": measured,
        "bytes": measured["bytes"],
        "sha256": media.sha256_file(path),
    }
    if recipe.source_title:
        source = index[recipe.source_title]
        record["source"] = {
            "title": source["title"],
            "url": source["description_url"],
            "author": source["author"],
            "license": source["license"],
            "license_url": source["license_url"],
            "description": source["description"],
            "changes": recipe.source_changes,
        }
    if recipe.transcript:
        record["transcript"] = recipe.transcript
    assert record["sha256"], f"{recipe.name}: empty digest"
    return record


def reset_fixtures_dir():
    """Delete the previously generated fixture tree."""
    assert config.FIXTURES_DIR.parent == config.PROJECT_DIR, (
        "reset: outside project"
    )
    assert config.FIXTURES_DIR.name == "fixtures", "reset: unexpected directory"
    if config.FIXTURES_DIR.is_dir():
        shutil.rmtree(config.FIXTURES_DIR)
    config.FIXTURES_DIR.mkdir(parents=True)
    assert config.FIXTURES_DIR.is_dir(), "reset: not a directory"


def generate(args):
    """Build every selected fixture and write the reports."""
    selected = select(args.filter)
    print(f"generating {len(selected)} fixtures")
    reset_fixtures_dir()
    titles = sorted(
        {recipe.source_title for recipe in selected if recipe.source_title}
    )
    index = {}
    if titles:
        index = commons.ensure_index(titles, refresh=args.refresh_sources)
    records = []
    for recipe in selected:
        recipe.builder(recipe, index)
        measured = probe(recipe)
        assert_matches(recipe, measured)
        records.append(build_record(recipe, measured, index))
        print(f"  {recipe.name} ({measured['bytes']} bytes)")
    if titles:
        commons.save_index({title: index[title] for title in titles})
    if args.filter:
        print("filtered run: reports not written")
        return 0
    report.write_all(records)
    print(
        "wrote manifest.json, checksums.txt, EXPECTED.md, ATTRIBUTION.md, "
        "TRANSCRIPTS.md"
    )
    return verify()


def verify():
    """Re-measure every shipped fixture and compare against the manifest."""
    manifest = report.load_manifest()
    recorded = {item["path"]: item for item in manifest["fixtures"]}
    on_disk = sorted(
        path.relative_to(config.FIXTURES_DIR).as_posix()
        for path in config.FIXTURES_DIR.rglob("*")
        if path.is_file()
    )
    if sorted(recorded) != on_disk:
        extra = sorted(set(on_disk) - set(recorded))
        missing = sorted(set(recorded) - set(on_disk))
        raise FixtureError(
            f"fixture list differs: extra={extra} missing={missing}"
        )
    for item in manifest["fixtures"]:
        path = config.FIXTURES_DIR / item["path"]
        digest = media.sha256_file(path)
        if digest != item["sha256"]:
            raise FixtureError(f"{item['path']}: checksum changed")
        measured = PROBES[item["kind"]](path)
        if measured != item["properties"]:
            raise FixtureError(
                f"{item['path']}: properties changed\n"
                f"  recorded {item['properties']}\n  measured {measured}"
            )
    total_kib = sum(item["bytes"] for item in manifest["fixtures"]) / 1024
    print(f"verified {manifest['count']} fixtures, {total_kib:.1f} KiB")
    return 0


def list_fixtures(args):
    """Print the inventory without touching the filesystem."""
    for recipe in select(args.filter):
        origin = recipe.source_title or "generated"
        print(f"{recipe.name}  [{recipe.kind}, {origin}]")
        print(f"    {recipe.description}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verify",
        action="store_true",
        help="check the shipped fixtures against manifest.json",
    )
    parser.add_argument(
        "--list", action="store_true", help="print the fixture inventory"
    )
    parser.add_argument(
        "--refresh-sources",
        action="store_true",
        help="re-fetch Commons metadata and checksums",
    )
    parser.add_argument(
        "--filter",
        action="append",
        default=[],
        help="only recipes whose name starts with this prefix",
    )
    args = parser.parse_args(argv)
    if args.list:
        return list_fixtures(args)
    if args.verify:
        return verify()
    return generate(args)


if __name__ == "__main__":
    sys.exit(main())
