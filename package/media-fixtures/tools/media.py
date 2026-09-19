"""Subprocess wrappers and media probes used by the fixture builders."""

import hashlib
import json
import subprocess
from pathlib import Path

COMMAND_TIMEOUT_S = 900
HASH_CHUNK_BYTES = 1 << 20
IMAGE_FORMAT_STRING = "%m|%w|%h|%z|%[colorspace]|%[type]|%n\n"
PRODUCERS = ("magick", "ffmpeg", "espeak-ng")

# Written into every produced file so that rerunning a builder reproduces the
# bytes: ImageMagick stamps PNG chunks with the creation date, and the FFmpeg
# muxers otherwise embed the current time, encoder version strings and random
# stream identifiers.
# A flag and its value stay on one line: they are read as pairs.
# fmt: off
REPRODUCIBLE_IMAGE_ARGUMENTS = (
    "-seed", "42",
    "-define", "png:exclude-chunk=date,time",
)
REPRODUCIBLE_MEDIA_ARGUMENTS = (
    "-fflags", "+bitexact",
    "-flags:v", "+bitexact",
    "-flags:a", "+bitexact",
)
# fmt: on


class MediaError(RuntimeError):
    """A media command failed or produced an unusable file."""


def run_command(argv):
    """Run `argv`, raise `MediaError` on failure, return stdout."""
    assert argv, "run_command: argv is empty"
    assert all(isinstance(item, str) for item in argv), "run_command: argv type"
    completed = subprocess.run(
        argv,
        check=False,
        capture_output=True,
        text=True,
        timeout=COMMAND_TIMEOUT_S,
    )
    if completed.returncode != 0:
        lines = (completed.stderr or "").strip().splitlines()
        detail = lines[-1] if lines else "no stderr"
        raise MediaError(f"{argv[0]} exited {completed.returncode}: {detail}")
    return completed.stdout


def produce(target, argv):
    """Run a `magick` or `ffmpeg` command that must create `target`.

    Reproducibility options are injected here rather than repeated in every
    builder, so two runs over the same inputs produce the same bytes.
    """
    assert isinstance(target, Path), "produce: target type"
    assert argv[0] in PRODUCERS, f"produce: tool {argv[0]}"
    arguments = list(argv)
    if arguments[0] == "magick":
        arguments[1:1] = list(REPRODUCIBLE_IMAGE_ARGUMENTS)
    if arguments[0] == "ffmpeg":
        assert arguments[-1] == str(target), "produce: ffmpeg target last"
        arguments[-1:-1] = list(REPRODUCIBLE_MEDIA_ARGUMENTS)
    target.parent.mkdir(parents=True, exist_ok=True)
    run_command(arguments)
    if not target.is_file():
        raise MediaError(f"{argv[0]} did not create {target}")
    assert target.stat().st_size > 0, f"produce: empty {target}"
    return target


def sha256_file(path):
    """Return the hex digest of a regular file."""
    assert Path(path).is_file(), f"sha256_file: missing {path}"
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while True:
            chunk = handle.read(HASH_CHUNK_BYTES)
            if not chunk:
                break
            digest.update(chunk)
    text = digest.hexdigest()
    assert len(text) == 64, "sha256_file: digest width"
    return text


def probe_image(path):
    """Return the measurable properties of an image file."""
    assert Path(path).is_file(), f"probe_image: missing {path}"
    raw = run_command(
        ["magick", "identify", "-format", IMAGE_FORMAT_STRING, str(path)]
    )
    lines = [line for line in raw.splitlines() if line.strip()]
    assert lines, f"probe_image: no frames in {path}"
    format_name, width, height, depth, colorspace, image_type, _ = lines[
        0
    ].split("|")
    properties = {
        "format": format_name,
        "width": int(width),
        "height": int(height),
        "depth": int(depth),
        "colorspace": colorspace,
        "type": image_type,
        "frames": len(lines),
        "bytes": Path(path).stat().st_size,
    }
    assert properties["width"] > 0, "probe_image: zero width"
    assert properties["frames"] == len(lines), "probe_image: frame count"
    return properties


def probe_animation(path):
    """Return codec, geometry and frame count of an animated image."""
    assert Path(path).is_file(), f"probe_animation: missing {path}"
    raw = run_command(
        [
            "ffprobe",
            "-v",
            "error",
            "-count_frames",
            "-select_streams",
            "v:0",
            "-show_streams",
            "-of",
            "json",
            str(path),
        ]
    )
    stream = json.loads(raw)["streams"][0]
    frames = stream.get("nb_read_frames")
    if not frames:
        raise MediaError(f"probe_animation: no frame count for {path}")
    properties = {
        "codec": stream["codec_name"],
        "width": int(stream["width"]),
        "height": int(stream["height"]),
        "frames": int(frames),
        "bytes": Path(path).stat().st_size,
    }
    assert properties["frames"] > 1, f"probe_animation: static file {path}"
    return properties


def probe_media(path):
    """Return container, codec, geometry and duration of audio or video."""
    assert Path(path).is_file(), f"probe_media: missing {path}"
    raw = run_command(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_format",
            "-show_streams",
            "-of",
            "json",
            str(path),
        ]
    )
    data = json.loads(raw)
    streams = data.get("streams", [])
    assert streams, f"probe_media: no streams in {path}"
    container = data["format"]
    video = []
    attached_pictures = 0
    for item in streams:
        if item.get("codec_type") != "video":
            continue
        if item.get("disposition", {}).get("attached_pic") == 1:
            attached_pictures += 1
        else:
            video.append(item)
    audio = [item for item in streams if item.get("codec_type") == "audio"]
    subtitle = [
        item for item in streams if item.get("codec_type") == "subtitle"
    ]
    properties = {
        "format": container["format_name"],
        "duration_s": round(float(container["duration"]), 3),
        "bytes": int(container["size"]),
        "audio_tracks": len(audio),
        "subtitle_tracks": len(subtitle),
        "cover_art": attached_pictures,
    }
    if video:
        properties["width"] = int(video[0]["width"])
        properties["height"] = int(video[0]["height"])
        properties["video_codec"] = video[0]["codec_name"]
    if audio:
        properties["audio_codec"] = audio[0]["codec_name"]
        properties["sample_rate"] = int(audio[0]["sample_rate"])
        properties["channels"] = int(audio[0]["channels"])
    return properties


def probe_text(path):
    """Return byte size and newline count of a text fixture."""
    assert Path(path).is_file(), f"probe_text: missing {path}"
    data = Path(path).read_bytes()
    return {"bytes": len(data), "lines": data.count(b"\n")}
