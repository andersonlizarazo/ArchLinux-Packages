"""Builders that create the fixture files.

Every builder takes its recipe (for options and the target path) and returns
the written path. `generate.py` measures the returned file and asserts the
measurement against the recipe's declared expectations.
"""

import commons
import config
import media

ANIMATION_COLORS = (
    "#d02020",
    "#e07000",
    "#c8b000",
    "#40a020",
    "#00a0a0",
    "#2050d0",
    "#8030c0",
    "#d02080",
    "#603010",
    "#101820",
)
PAGES = ("1", "2", "3")
SUBTRACTIVE_GRADIENT = ("#102040", "#e0c090")
SUBTITLE_SRT = (
    "1\n00:00:00,500 --> 00:00:02,000\nFirst cue line.\n\n"
    "2\n00:00:02,200 --> 00:00:03,800\nSecond cue line.\n"
)
SUBTITLE_VTT = (
    "WEBVTT\n\n00:00:00.500 --> 00:00:02.000\nFirst cue line.\n\n"
    "00:00:02.200 --> 00:00:03.800\nSecond cue line.\n"
)


def target_of(recipe):
    """Return the output path of a recipe."""
    assert recipe.name, "target_of: name"
    assert "/" in recipe.name, f"target_of: unqualified {recipe.name}"
    return config.FIXTURES_DIR / recipe.name


def write_bytes(recipe, data):
    """Write raw bytes to the recipe target."""
    assert isinstance(data, bytes), "write_bytes: data type"
    target = target_of(recipe)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    assert target.stat().st_size == len(data), "write_bytes: short write"
    return target


def commons_source(index, recipe):
    """Download the pinned Commons original once and return its path."""
    assert recipe.source_title in index, f"{recipe.name}: unpinned source"
    return commons.ensure_source(index, recipe)


# --- images ---------------------------------------------------------------


def build_commons_image(recipe, index):
    """Resize a Commons photo, keeping its metadata profiles."""
    source = commons_source(index, recipe)
    target = target_of(recipe)
    width_max = recipe.options["width_max"]
    quality = recipe.options["quality"]
    assert width_max > 0, "build_commons_image: width_max"
    assert 1 <= quality <= 100, "build_commons_image: quality"
    return media.produce(
        target,
        [
            "magick",
            str(source),
            "-resize",
            f"{width_max}x{width_max}>",
            "-quality",
            str(quality),
            f"JPEG:{target}",
        ],
    )


def build_alpha_gradient(recipe, index):
    """Fractal colour fading to transparent: alpha and compositing."""
    target = target_of(recipe)
    return media.produce(
        target,
        [
            "magick",
            "-size",
            "256x256",
            "plasma:fractal",
            "-blur",
            "0x8",
            "-alpha",
            "set",
            "-channel",
            "A",
            "-fx",
            "1-j/h",
            "+channel",
            "png32:" + str(target),
        ],
    )


def build_gray_16bit(recipe, index):
    """Single-channel 16-bit grayscale: depth and colorspace handling."""
    target = target_of(recipe)
    return media.produce(
        target,
        [
            "magick",
            "-size",
            "128x128",
            "gradient:black-white",
            "-colorspace",
            "Gray",
            "-depth",
            "16",
            "PNG:" + str(target),
        ],
    )


def build_palette_image(recipe, index):
    """Indexed 8-bit PNG: palette and quantization code paths."""
    target = target_of(recipe)
    return media.produce(
        target,
        [
            "magick",
            "-size",
            "64x64",
            "plasma:fractal",
            "-colors",
            "16",
            "-depth",
            "8",
            "PNG8:" + str(target),
        ],
    )


def build_animation(recipe, index):
    """Ten-frame animation, written as GIF or APNG."""
    frames = []
    for index_color, color in enumerate(ANIMATION_COLORS):
        frames.extend(
            [
                "-size",
                "64x64",
                "-delay",
                "8",
                f"xc:{color}",
                "-fill",
                "#ffffff",
                "-draw",
                f"circle {8 + index_color * 5},32 {12 + index_color * 5},32",
            ]
        )
    prefix = recipe.options["prefix"]
    assert prefix in ("GIF", "APNG"), f"{recipe.name}: prefix {prefix}"
    target = target_of(recipe)
    return media.produce(
        target,
        [
            "magick",
            "-loop",
            "0",
            *frames,
            f"{prefix}:{target}",
        ],
    )


def build_multipage_tiff(recipe, index):
    """Three-page TIFF: multi-frame image containers."""
    target = target_of(recipe)
    pages = []
    for page in PAGES:
        pages.extend(
            [
                "-size",
                "200x150",
                "xc:#ffffff",
                "-gravity",
                "center",
                "-pointsize",
                "48",
                "-fill",
                "#202020",
                "-draw",
                f"text 0,0 '{page}'",
            ]
        )
    return media.produce(
        target,
        [
            "magick",
            "-compress",
            "LZW",
            *pages,
            f"TIFF:{target}",
        ],
    )


def build_cmyk_jpeg(recipe, index):
    """CMYK JPEG: non-RGB colorspace conversion."""
    target = target_of(recipe)
    return media.produce(
        target,
        [
            "magick",
            "-size",
            "200x200",
            "gradient:#00ffff-#101010",
            "-colorspace",
            "CMYK",
            "-quality",
            "85",
            f"JPEG:{target}",
        ],
    )


def build_large_jpeg(recipe, index):
    """Large smooth JPEG: resize and resample benchmarks."""
    target = target_of(recipe)
    return media.produce(
        target,
        [
            "magick",
            "-size",
            "4000x3000",
            "gradient:" + "-".join(SUBTRACTIVE_GRADIENT),
            "-quality",
            "80",
            f"JPEG:{target}",
        ],
    )


def build_single_pixel(recipe, index):
    """One transparent-free pixel: degenerate geometry."""
    target = target_of(recipe)
    return media.produce(
        target,
        [
            "magick",
            "-size",
            "1x1",
            "xc:#ff0000",
            "PNG24:" + str(target),
        ],
    )


def build_plain_png(recipe, index):
    """Small opaque PNG, reused as an odd-name payload."""
    target = target_of(recipe)
    size = recipe.options.get("size", "32x32")
    return media.produce(
        target,
        [
            "magick",
            "-size",
            size,
            "xc:#4080c0",
            "-fill",
            "#ffe0a0",
            "-draw",
            "rectangle 4,4 28,28",
            "PNG24:" + str(target),
        ],
    )


def build_rendered_text(recipe, index):
    """Rendered text: OCR and glyph-coverage testing."""
    target = target_of(recipe)
    return media.produce(
        target,
        [
            "magick",
            "-size",
            "480x120",
            "xc:#f4f4f4",
            "-gravity",
            "center",
            "-pointsize",
            "30",
            "-fill",
            "#101010",
            "-annotate",
            "0",
            "The quick brown fox 0123456789",
            "PNG24:" + str(target),
        ],
    )


def build_webp_lossy(recipe, index):
    """Lossy WebP: modern lossy-in-container decoding."""
    target = target_of(recipe)
    return media.produce(
        target,
        [
            "magick",
            "-size",
            "256x256",
            "radial-gradient:#ffffff-#204080",
            "-quality",
            "75",
            f"WEBP:{target}",
        ],
    )


def build_webp_alpha(recipe, index):
    """Lossless WebP with alpha: the alpha-capable WebP path."""
    target = target_of(recipe)
    return media.produce(
        target,
        [
            "magick",
            "-size",
            "256x256",
            "gradient:#00000000-#ff8800ff",
            "-define",
            "webp:lossless=true",
            f"WEBP:{target}",
        ],
    )


def build_avif(recipe, index):
    """AVIF: HEIF-family container, delegate-dependent."""
    target = target_of(recipe)
    return media.produce(
        target,
        [
            "magick",
            "-size",
            "256x192",
            "gradient:#123456-#abcdef",
            "-quality",
            "60",
            f"AVIF:{target}",
        ],
    )


def build_jpeg_xl(recipe, index):
    """JPEG XL: newest still-image codec in the set."""
    target = target_of(recipe)
    return media.produce(
        target,
        [
            "magick",
            "-size",
            "256x192",
            "plasma:fractal",
            "-quality",
            "90",
            f"JXL:{target}",
        ],
    )


def build_svg(recipe, index):
    """Hand-written SVG: vector input with text and gradients."""
    svg = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" width="300" height="200"'
        ' viewBox="0 0 300 200">\n'
        "  <defs>\n"
        '    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">\n'
        '      <stop offset="0" stop-color="#1b3a6b"/>\n'
        '      <stop offset="1" stop-color="#f0c86a"/>\n'
        "    </linearGradient>\n"
        "  </defs>\n"
        '  <rect width="300" height="200" fill="url(#sky)"/>\n'
        '  <circle cx="220" cy="55" r="28" fill="#fff3c4"/>\n'
        '  <path d="M0 200 L90 110 L150 200 Z" fill="#2d2d34"/>\n'
        '  <path d="M110 200 L190 120 L300 200 Z" fill="#3b3b45"/>\n'
        '  <text x="12" y="190" font-family="sans-serif" font-size="16"'
        ' fill="#ffffff">media fixtures</text>\n'
        "</svg>\n"
    )
    return write_bytes(recipe, svg.encode("utf-8"))


# --- audio ----------------------------------------------------------------


def build_cover_art():
    """Build the JPEG used as embedded cover art."""
    target = config.CACHE_DIR / "cover-200.jpg"
    return media.produce(
        target,
        [
            "magick",
            "-size",
            "200x200",
            "gradient:#204060-#c0a060",
            "-quality",
            "80",
            f"JPEG:{target}",
        ],
    )


def build_commons_audio(recipe, index):
    """Trim and re-encode a Commons audio file."""
    source = commons_source(index, recipe)
    target = target_of(recipe)
    start_s = recipe.options["start_s"]
    duration_s = recipe.options["duration_s"]
    assert duration_s > 0, "build_commons_audio: duration"
    return media.produce(
        target,
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            str(start_s),
            "-t",
            str(duration_s),
            "-i",
            str(source),
            *recipe.options["encoder"],
            "-y",
            str(target),
        ],
    )


def build_tagged_audio(recipe, index):
    """Encode audio with text tags and attached cover art."""
    source = commons_source(index, recipe)
    target = target_of(recipe)
    cover = build_cover_art()
    argv = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-ss",
        str(recipe.options["start_s"]),
        "-t",
        str(recipe.options["duration_s"]),
        "-i",
        str(source),
        "-i",
        str(cover),
        "-map",
        "0:a:0",
        "-map",
        "1:v:0",
        "-c:v",
        "copy",
        "-disposition:v:0",
        "attached_pic",
    ]
    tags = recipe.options["tags"]
    assert tags, "build_tagged_audio: tags"
    for key, value in sorted(tags.items()):
        argv.extend(["-metadata", f"{key}={value}"])
    argv.extend(recipe.options["encoder"])
    argv.extend(["-y", str(target)])
    return media.produce(target, argv)


def build_synthetic_speech(recipe, index):
    """Synthesize speech with espeak-ng, then resample."""
    spoken = config.CACHE_DIR / "speech-espeak.wav"
    target = target_of(recipe)
    media.produce(
        spoken,
        [
            "espeak-ng",
            "-v",
            "en-us",
            "-s",
            "150",
            "-w",
            str(spoken),
            recipe.options["text"],
        ],
    )
    return media.produce(
        target,
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(spoken),
            "-ar",
            str(recipe.options["sample_rate"]),
            "-ac",
            str(recipe.options["channels"]),
            "-c:a",
            "pcm_s16le",
            "-y",
            str(target),
        ],
    )


# --- video ----------------------------------------------------------------


def build_synthetic_clip(recipe, index):
    """Test pattern plus tone, encoded into the requested container."""
    target = target_of(recipe)
    duration_s = recipe.options["duration_s"]
    return media.produce(
        target,
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "lavfi",
            "-i",
            f"testsrc2=size={recipe.options['size']}:rate="
            f"{recipe.options['rate']}:duration={duration_s}",
            "-f",
            "lavfi",
            "-i",
            f"sine=frequency=440:sample_rate=44100:duration={duration_s}",
            *recipe.options["encoder"],
            "-shortest",
            "-y",
            str(target),
        ],
    )


def build_silent_clip(recipe, index):
    """Video-only clip: no audio stream at all."""
    target = target_of(recipe)
    duration_s = recipe.options["duration_s"]
    return media.produce(
        target,
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "lavfi",
            "-i",
            f"testsrc2=size={recipe.options['size']}:rate="
            f"{recipe.options['rate']}:duration={duration_s}",
            *recipe.options["encoder"],
            "-an",
            "-y",
            str(target),
        ],
    )


def build_counter_clip(recipe, index):
    """Burn the frame number and timestamp into every frame."""
    target = target_of(recipe)
    duration_s = recipe.options["duration_s"]
    draw = (
        "drawtext=text='frame %{frame_num}  %{pts\\:hms}':"
        "x=10:y=10:fontsize=24:fontcolor=white:box=1:boxcolor=black@0.5"
    )
    return media.produce(
        target,
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "lavfi",
            "-i",
            f"testsrc2=size={recipe.options['size']}:rate="
            f"{recipe.options['rate']}:duration={duration_s}",
            "-f",
            "lavfi",
            "-i",
            "anullsrc=r=44100:cl=stereo",
            "-vf",
            draw,
            *recipe.options["encoder"],
            "-t",
            str(duration_s),
            "-shortest",
            "-y",
            str(target),
        ],
    )


def build_commons_clip(recipe, index):
    """Trim and re-encode a Commons video clip."""
    source = commons_source(index, recipe)
    target = target_of(recipe)
    return media.produce(
        target,
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            str(recipe.options["start_s"]),
            "-t",
            str(recipe.options["duration_s"]),
            "-i",
            str(source),
            "-vf",
            f"scale={recipe.options['width']}:-2",
            *recipe.options["encoder"],
            "-y",
            str(target),
        ],
    )


def build_multitrack_mkv(recipe, index):
    """Matroska file with two audio tracks and one subtitle track."""
    target = target_of(recipe)
    cache = config.CACHE_DIR
    video = cache / "multitrack-video.mp4"
    tones = (cache / "multitrack-eng.wav", cache / "multitrack-jpn.wav")
    subtitles = cache / "multitrack.srt"
    media.produce(
        video,
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "lavfi",
            "-i",
            "testsrc2=size=320x240:rate=25:duration=4",
            "-c:v",
            "libx264",
            "-crf",
            "32",
            "-pix_fmt",
            "yuv420p",
            "-an",
            "-y",
            str(video),
        ],
    )
    for tone, frequency in zip(tones, (440, 660), strict=True):
        media.produce(
            tone,
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-f",
                "lavfi",
                "-i",
                f"sine=frequency={frequency}:duration=4",
                "-ac",
                "1",
                "-ar",
                "48000",
                "-c:a",
                "pcm_s16le",
                "-y",
                str(tone),
            ],
        )
    subtitles.parent.mkdir(parents=True, exist_ok=True)
    subtitles.write_text(SUBTITLE_SRT, encoding="utf-8")
    assert subtitles.stat().st_size > 0, "build_multitrack_mkv: subtitles"
    return media.produce(
        target,
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(video),
            "-i",
            str(tones[0]),
            "-i",
            str(tones[1]),
            "-i",
            str(subtitles),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-map",
            "2:a:0",
            "-map",
            "3:s:0",
            "-c:v",
            "copy",
            "-c:a",
            "libopus",
            "-b:a",
            "48k",
            "-c:s",
            "srt",
            "-metadata:s:a:0",
            "language=eng",
            "-metadata:s:a:0",
            "title=English tone",
            "-metadata:s:a:1",
            "language=jpn",
            "-metadata:s:a:1",
            "title=Japanese tone",
            "-y",
            str(target),
        ],
    )


# --- text and odd files ---------------------------------------------------


def build_unicode_torture(recipe, index):
    """One line per Unicode class that breaks naive text handling."""
    lines = [
        "ASCII: The quick brown fox jumps over the lazy dog.",
        "Latin accents: café, naïve, Straße, smørrebrød, łódź, řeka",
        "CJK: 日本語のテキスト、中文字符、한국어 문장",
        "Emoji: 🎬 🎵 🖼️ 👍🏽 👨‍👩‍👧‍👦 🇯🇵 🏳️‍🌈",
        "RTL: العربية نص عربي. עברית טקסט.",
        "Combining: a\u0301 e\u0301 n\u0303 versus precomposed "
        "\u00e1 \u00e9 \u00f1",
        "Zero width: a\u200bb\u200cc\ufeffd (ZWSP, ZWNJ, ZWNBSP)",
        "Symbols: ∑ ∫ √ ≠ ≤ ≥ ∞ → ° ½ © ® ™",
        "Quotes: “curly” ‘single’ „low“ «guillemets» 「corner」",
        "Fullwidth: ＡＢＣ１２３",
        "Control: tab\there and a line separator\u2028inside a line",
    ]
    body = "\n".join(lines) + "\n"
    prefix = recipe.options.get("bom", False)
    if prefix:
        return write_bytes(recipe, b"\xef\xbb\xbf" + body.encode("utf-8"))
    return write_bytes(recipe, body.encode("utf-8"))


def build_crlf(recipe, index):
    """Windows line endings: CRLF handling in readers."""
    lines = ["first line", "second line", "third line", ""]
    return write_bytes(recipe, "\r\n".join(lines).encode("utf-8"))


def build_no_final_newline(recipe, index):
    """File whose last line has no terminator."""
    body = "last line has no newline\nsecond to last has one\nend"
    return write_bytes(recipe, body.encode("utf-8"))


def build_latin1(recipe, index):
    """Non-UTF-8 single-byte text: encoding detection."""
    body = "Caf\xe9, na\xefve, Stra\xdfe, \xc5ngstr\xf6m\n".encode("latin-1")
    return write_bytes(recipe, body)


def build_nul_bytes(recipe, index):
    """Embedded NUL bytes: breaks naive line and string handling."""
    return write_bytes(recipe, b"before\x00after\nsecond\x00line\n")


def build_long_line(recipe, index):
    """One very long line: buffer and wrapping limits."""
    return write_bytes(recipe, b"a" * 100_000 + b"\n")


def build_subtitles(recipe, index):
    """Subtitle file in SubRip or WebVTT format."""
    if recipe.options["format"] == "srt":
        return write_bytes(recipe, SUBTITLE_SRT.encode("utf-8"))
    return write_bytes(recipe, SUBTITLE_VTT.encode("utf-8"))


def build_odd_text(recipe, index):
    """Small text file with an adversarial name."""
    return write_bytes(recipe, f"fixture for {recipe.name}\n".encode())


def build_png_named_jpg(recipe, index):
    """PNG bytes behind a .jpg extension: content sniffing."""
    temporary = config.CACHE_DIR / "odd-plain.png"
    media.produce(
        temporary,
        [
            "magick",
            "-size",
            "48x48",
            "xc:#20a060",
            "PNG24:" + str(temporary),
        ],
    )
    return write_bytes(recipe, temporary.read_bytes())


def build_truncated_jpeg(recipe, index):
    """JPEG cut short: error handling for damaged input."""
    temporary = config.CACHE_DIR / "odd-full.jpg"
    media.produce(
        temporary,
        [
            "magick",
            "-size",
            "300x300",
            "plasma:fractal",
            "-quality",
            "90",
            f"JPEG:{temporary}",
        ],
    )
    data = temporary.read_bytes()
    assert len(data) > 4096, "build_truncated_jpeg: source too small"
    return write_bytes(recipe, data[:2048])


def build_zero_bytes(recipe, index):
    """Empty file: the degenerate input every reader must reject."""
    return write_bytes(recipe, b"")


def build_no_extension(recipe, index):
    """JPEG bytes with no extension: format detection without a hint."""
    temporary = config.CACHE_DIR / "odd-extensionless.jpg"
    media.produce(
        temporary,
        [
            "magick",
            "-size",
            "120x80",
            "gradient:#334455-#ddeeff",
            "-quality",
            "80",
            f"JPEG:{temporary}",
        ],
    )
    return write_bytes(recipe, temporary.read_bytes())


def build_text_size_chart(recipe, index):
    """One sentence drawn at six point sizes: legibility and OCR scales."""
    target = target_of(recipe)
    lines = recipe.options["lines"]
    offsets = (14, 34, 62, 104, 170, 280)
    assert len(lines) == len(offsets), "build_text_size_chart: line count"
    arguments = [
        "magick",
        "-size",
        "640x360",
        "xc:#ffffff",
        "-fill",
        "#101010",
        "-gravity",
        "northwest",
    ]
    for (pointsize, drawn_text), offset in zip(lines, offsets, strict=True):
        arguments.extend(
            [
                "-pointsize",
                str(pointsize),
                "-annotate",
                f"+14+{offset}",
                drawn_text,
            ]
        )
    arguments.append("PNG24:" + str(target))
    return media.produce(target, arguments)
