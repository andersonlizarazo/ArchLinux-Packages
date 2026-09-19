"""Unit tests for the fixture toolchain.

These cover the pure logic: declaration checking, recipe selection, record
formatting and download selection. Building media is exercised by
`generate.py --verify`, which runs against the committed fixtures.
"""

import commons
import config
import generate
import media
import pytest
import recipes
import report

IMAGE_RECORD = {
    "title": "File:Example.jpg",
    "original_url": "https://upload.wikimedia.org/example.jpg",
    "thumbnail_url": "https://upload.wikimedia.org/thumb/example.jpg",
    "original_bytes": config.ORIGINAL_BYTES_MAX + 1,
    "mime": "image/jpeg",
}
AUDIO_RECORD = dict(
    IMAGE_RECORD,
    title="File:Example.ogg",
    original_url="https://upload.wikimedia.org/example.ogg",
    mime="audio/ogg",
)


def make_recipe(**overrides):
    """Return a recipe with test expectations."""
    fields = {
        "name": "images/test.png",
        "kind": "image",
        "description": "test fixture",
        "builder": None,
        "expected": {"format": "PNG", "width": 8},
    }
    fields.update(overrides)
    return recipes.Recipe(**fields)


def test_assert_matches_accepts_matching_measurement():
    recipe = make_recipe()
    generate.assert_matches(recipe, {"format": "PNG", "width": 8})


def test_assert_matches_rejects_wrong_value():
    recipe = make_recipe()
    with pytest.raises(generate.FixtureError, match="width"):
        generate.assert_matches(recipe, {"format": "PNG", "width": 9})


def test_assert_matches_rejects_missing_property():
    recipe = make_recipe(expected={"channels": 2})
    with pytest.raises(generate.FixtureError, match="probe has no channels"):
        generate.assert_matches(recipe, {"format": "PNG", "width": 8})


def test_assert_matches_honours_upper_bound():
    recipe = make_recipe(expected={"bytes_max": 100})
    generate.assert_matches(recipe, {"bytes": 100})
    with pytest.raises(generate.FixtureError, match="bytes"):
        generate.assert_matches(recipe, {"bytes": 101})


def test_assert_matches_honours_lower_bound():
    recipe = make_recipe(expected={"duration_s_min": 2.0})
    generate.assert_matches(recipe, {"duration_s": 2.0})
    with pytest.raises(generate.FixtureError, match="duration_s"):
        generate.assert_matches(recipe, {"duration_s": 1.5})


def test_assert_matches_tolerates_duration_drift():
    recipe = make_recipe(expected={"duration_s": 5.0})
    generate.assert_matches(recipe, {"duration_s": 5.0 + 0.001})
    with pytest.raises(generate.FixtureError, match="duration_s"):
        generate.assert_matches(recipe, {"duration_s": 5.0 + 1.0})


def test_select_returns_every_recipe_by_default():
    assert generate.select([]) == list(recipes.RECIPES)


def test_select_filters_by_prefix():
    chosen = generate.select(["text/"])
    assert chosen
    assert all(recipe.name.startswith("text/") for recipe in chosen)


def test_select_rejects_unknown_prefix():
    with pytest.raises(generate.FixtureError, match="no recipe matches"):
        generate.select(["nothing/"])


def test_download_url_prefers_thumbnail_for_large_images():
    assert commons.download_url(IMAGE_RECORD).endswith("/thumb/example.jpg")


def test_download_url_keeps_large_audio_original():
    # Commons serves a generic file-type icon as the thumbnail of audio.
    assert commons.download_url(AUDIO_RECORD).endswith("/example.ogg")


def test_download_url_keeps_small_originals():
    small = dict(IMAGE_RECORD, original_bytes=1024)
    assert commons.download_url(small).endswith("/example.jpg")


def test_cache_path_uses_the_url_file_name():
    path = commons.cache_path("https://upload.wikimedia.org/a/Some_File.jpg")
    assert path.name == "Some_File.jpg"


def test_plain_text_strips_markup_and_collapses_space():
    markup = "<p>Eduard&nbsp;Spelterini<br/>1904</p>"
    assert commons.plain_text(markup) == "Eduard Spelterini 1904"


def test_summarise_skips_absent_properties():
    summary = report.summarise({"format": "PNG", "width": 8, "bytes": 40})
    assert summary == "format=PNG, width=8"


def test_shorten_cuts_on_a_word_boundary():
    text = "one two three four five"
    shortened = report.shorten(text, 12)
    assert shortened.endswith("…")
    assert len(shortened) <= 12


def test_shorten_keeps_short_text_unchanged():
    assert report.shorten("short", 20) == "short"


def test_probe_text_counts_bytes_and_newlines(tmp_path):
    path = tmp_path / "sample.txt"
    path.write_bytes(b"one\ntwo\n")
    assert media.probe_text(path) == {"bytes": 8, "lines": 2}


def test_recipes_are_well_formed():
    names = [recipe.name for recipe in recipes.RECIPES]
    assert len(names) == len(set(names))
    for recipe in recipes.RECIPES:
        assert recipe.name.count("/") >= 1, recipe.name
        assert recipe.kind in generate.PROBES, recipe.name
        assert recipe.expected, recipe.name
        assert recipe.description.endswith("."), recipe.name
        assert callable(recipe.builder), recipe.name


def test_downloaded_recipes_record_their_changes():
    for recipe in recipes.RECIPES:
        if recipe.source_title:
            assert recipe.source_changes, recipe.name
            assert recipe.source_title.startswith("File:"), recipe.name


def test_speech_fixtures_declare_a_transcript():
    """Every fixture that carries speech must say what it says."""
    spoken = (
        "audio/speech-armstrong-1969.ogg",
        "audio/speech-synthetic-8k.wav",
        "video/speaking-cdc-interview-6s.mp4",
    )
    declared = {recipe.name: recipe.transcript for recipe in recipes.RECIPES}
    for name in spoken:
        assert name in declared, name
        assert declared[name], name


def test_transcripts_have_no_leading_or_trailing_blank_lines():
    for recipe in recipes.RECIPES:
        if recipe.transcript:
            assert recipe.transcript == recipe.transcript.strip(), recipe.name


def test_chart_transcript_matches_the_drawn_lines():
    drawn = "\n".join(text for _, text in recipes.TEXT_CHART_LINES)
    assert drawn == recipes.TEXT_CHART_TRANSCRIPT


def test_build_record_keeps_the_transcript(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "FIXTURES_DIR", tmp_path)
    recipe = make_recipe(transcript="exact words")
    path = tmp_path / recipe.name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"payload")
    record = generate.build_record(recipe, {"bytes": 7}, {})
    assert record["transcript"] == "exact words"


def test_build_record_omits_an_empty_transcript(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "FIXTURES_DIR", tmp_path)
    recipe = make_recipe()
    path = tmp_path / recipe.name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"payload")
    record = generate.build_record(recipe, {"bytes": 7}, {})
    assert "transcript" not in record
