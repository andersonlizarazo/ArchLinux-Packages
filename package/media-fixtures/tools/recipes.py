"""The single registry of every fixture: what it is and what it must be.

The engine asserts each measured file against `expected`, so a wrong value
here fails the build instead of shipping a fixture that no longer matches its
documentation.
"""

from dataclasses import dataclass, field

import builders

GIZA = "File:Spelterini Pyramids.jpg"
PORTRAIT = "File:Élisabeth de Caraman-Chimay (1860-1952) A.jpg"
BIRD = "File:Melanopareia maximiliani 1847.jpg"
CAT = (
    "File:Photograph of First Lady Hillary Rodham Clinton and Socks the Cat- "
    "12-13-1995 (6461521265) (cropped).jpg"
)
POPPY = "File:Poppy bloom in the Red Hills (27779604147).jpg"
MUSIC = "File:Bach Partita 3 for Violin Prelude 01.wav"
ARMSTRONG = "File:Phrase de Neil Armstrong.oga"
CDC = "File:I Am CDC - Kiersten Kugeler.webm"
MARS = "File:NASA-JPL - PIA10149 (pd).ogv"
ERUPTION = (
    "File:Sarychev Peak eruption on 12 June 2009, oblique satellite view.ogv"
)

SPEECH_TEXT = (
    "The quick brown fox jumps over the lazy dog. "
    "Numbers: zero one two three. "
    "This recording is synthesized, so its wording never changes."
)

# The source page transcribes this recording of the first Moon landing.
ARMSTRONG_TEXT = (
    "That's one small step for [a] man, one giant leap for mankind."
)

# The source page quotes the opening words of the interview.
CDC_TEXT = (
    "I've been with CDC for 14 years. I'm an epidemiologist. "
    "I work in CDC's Division of Vector Borne Diseases."
)

TEXT_CHART_SENTENCE = "The quick brown fox jumps over the lazy dog."
# The builder draws exactly these lines, so the transcript cannot drift.
TEXT_CHART_LINES = (
    *(
        (pointsize, f"{TEXT_CHART_SENTENCE} ({pointsize} pt)")
        for pointsize in (8, 12, 18, 28)
    ),
    (48, "The quick brown fox"),
    (72, "The quick"),
)
TEXT_CHART_TRANSCRIPT = "\n".join(text for _, text in TEXT_CHART_LINES)

MUSIC_TAGS = {
    "artist": "Johann Sebastian Bach",
    "album": "media-fixtures reference recordings",
    "title": "Partita No. 3 for solo violin, Prelude (excerpt)",
    "date": "2020",
    "genre": "Classical",
    "comment": "Synthetic tag values for metadata testing.",
    "track": "1/1",
}


@dataclass(frozen=True)
class Recipe:
    """One fixture, its builder, and its declared properties."""

    name: str
    kind: str
    description: str
    builder: object
    expected: dict = field(default_factory=dict)
    options: dict = field(default_factory=dict)
    source_title: str = ""
    source_changes: str = ""
    transcript: str = ""


RECIPES = (
    # --- downloaded photographs and artwork ------------------------------
    Recipe(
        name="images/photo-giza-aerial-1904.jpg",
        kind="image",
        description=(
            "Balloon photograph of the Giza pyramids by Eduard Spelterini "
            "(1904). Real grain and tone, no embedded metadata."
        ),
        builder=builders.build_commons_image,
        options={"width_max": 1280, "quality": 82},
        expected={"format": "JPEG", "width": 1280, "bytes_max": 400_000},
        source_title=GIZA,
        source_changes="Resized to fit 1280 px, JPEG quality 82.",
    ),
    Recipe(
        name="images/photo-portrait-1895.jpg",
        kind="image",
        description=(
            "Studio portrait of Élisabeth de Caraman-Chimay "
            "(Paul Nadar, 1895), grayscale JPEG. Portrait orientation and "
            "skin detail for resampling tests."
        ),
        builder=builders.build_commons_image,
        options={"width_max": 900, "quality": 82},
        expected={"format": "JPEG", "height": 900, "bytes_max": 300_000},
        source_title=PORTRAIT,
        source_changes="Resized to fit 900 px, JPEG quality 82.",
    ),
    Recipe(
        name="images/lithograph-bird-1847.jpg",
        kind="image",
        description=(
            "Hand-coloured lithograph of Melanopareia maximiliani (1847). "
            "Fine detail and flat colour areas."
        ),
        builder=builders.build_commons_image,
        options={"width_max": 1100, "quality": 82},
        expected={"format": "JPEG", "width": 1100, "bytes_max": 500_000},
        source_title=BIRD,
        source_changes="Resized to fit 1100 px, JPEG quality 82.",
    ),
    Recipe(
        name="images/photo-cat-1995.jpg",
        kind="image",
        description=(
            "Photograph of Socks the Cat with Hillary Rodham Clinton "
            "(1995). Fur detail, a human face, and a busy background."
        ),
        builder=builders.build_commons_image,
        options={"width_max": 900, "quality": 82},
        expected={"format": "JPEG", "width": 900, "bytes_max": 300_000},
        source_title=CAT,
        source_changes="Resized to fit 900 px, JPEG quality 82.",
    ),
    Recipe(
        name="images/photo-poppy-red-hills-2016.jpg",
        kind="image",
        description=(
            "Dense bloom of yellow poppies in the Red Hills, Tuolumne County, "
            "California (2016). Saturated yellow flowers against green spring "
            "grass."
        ),
        builder=builders.build_commons_image,
        options={"width_max": 900, "quality": 82},
        expected={"format": "JPEG", "width": 900, "bytes_max": 300_000},
        source_title=POPPY,
        source_changes="Resized to fit 900 px, JPEG quality 82.",
    ),
    # --- generated images ------------------------------------------------
    Recipe(
        name="images/gradient-alpha-256.png",
        kind="image",
        description=(
            "Fractal colour with a vertical alpha fade: alpha channel and "
            "compositing."
        ),
        builder=builders.build_alpha_gradient,
        expected={
            "format": "PNG",
            "width": 256,
            "height": 256,
            "depth": 8,
            "type": "TrueColorAlpha",
            "frames": 1,
        },
    ),
    Recipe(
        name="images/gray-16bit-128.png",
        kind="image",
        description="16-bit single-channel grayscale gradient: bit depth.",
        builder=builders.build_gray_16bit,
        expected={
            "format": "PNG",
            "width": 128,
            "height": 128,
            "depth": 16,
            "colorspace": "Gray",
            "frames": 1,
        },
    ),
    Recipe(
        name="images/palette-16colors-64.png",
        kind="image",
        description="Indexed PNG with a 16-colour palette: palette handling.",
        builder=builders.build_palette_image,
        expected={
            "format": "PNG",
            "width": 64,
            "height": 64,
            "depth": 8,
            "type": "Palette",
        },
    ),
    Recipe(
        name="images/animation-10frames.gif",
        kind="animation",
        description="Ten-frame looping GIF: frame delays and disposal.",
        builder=builders.build_animation,
        options={"prefix": "GIF"},
        expected={"codec": "gif", "width": 64, "height": 64, "frames": 10},
    ),
    Recipe(
        name="images/animation-10frames.png",
        kind="animation",
        description="Same ten frames as an animated PNG (APNG).",
        builder=builders.build_animation,
        options={"prefix": "APNG"},
        expected={
            "codec": "apng",
            "width": 64,
            "height": 64,
            "frames": 10,
        },
    ),
    Recipe(
        name="images/multipage-3pages.tiff",
        kind="image",
        description="Three-page TIFF: multi-page readers and page selection.",
        builder=builders.build_multipage_tiff,
        expected={
            "format": "TIFF",
            "width": 200,
            "height": 150,
            "frames": 3,
        },
    ),
    Recipe(
        name="images/cmyk-200x200.jpg",
        kind="image",
        description="CMYK JPEG: subtractive colourspace conversion.",
        builder=builders.build_cmyk_jpeg,
        expected={
            "format": "JPEG",
            "width": 200,
            "height": 200,
            "colorspace": "CMYK",
        },
    ),
    Recipe(
        name="images/gradient-4000x3000.jpg",
        kind="image",
        description="4000x3000 JPEG: resizing, tiling and memory limits.",
        builder=builders.build_large_jpeg,
        expected={
            "format": "JPEG",
            "width": 4000,
            "height": 3000,
            "bytes_max": 700_000,
        },
    ),
    Recipe(
        name="images/pixel-1x1.png",
        kind="image",
        description="Single pixel: degenerate geometry, resize edge case.",
        builder=builders.build_single_pixel,
        expected={"format": "PNG", "width": 1, "height": 1},
    ),
    Recipe(
        name="images/text-rendered-480x120.png",
        kind="image",
        description="Rendered text: glyph coverage and OCR testing.",
        builder=builders.build_rendered_text,
        expected={"format": "PNG", "width": 480, "height": 120},
        transcript="The quick brown fox 0123456789",
    ),
    Recipe(
        name="images/text-sizes-chart-640x360.png",
        kind="image",
        description=(
            "One sentence drawn at 8, 12, 18, 28, 48 and 72 points: "
            "legibility, line height and OCR at several scales."
        ),
        builder=builders.build_text_size_chart,
        options={"lines": TEXT_CHART_LINES},
        expected={"format": "PNG", "width": 640, "height": 360},
        transcript=TEXT_CHART_TRANSCRIPT,
    ),
    Recipe(
        name="images/webp-lossy-256.webp",
        kind="image",
        description="Lossy WebP: modern still-image decoding.",
        builder=builders.build_webp_lossy,
        expected={"format": "WEBP", "width": 256, "height": 256},
    ),
    Recipe(
        name="images/webp-alpha-lossless-256.webp",
        kind="image",
        description="Lossless WebP with alpha.",
        builder=builders.build_webp_alpha,
        expected={"format": "WEBP", "width": 256, "height": 256},
    ),
    Recipe(
        name="images/avif-q60-256x192.avif",
        kind="image",
        description="AVIF: HEIF-family container, delegate dependent.",
        builder=builders.build_avif,
        expected={"format": "AVIF", "width": 256, "height": 192},
    ),
    Recipe(
        name="images/jxl-q90-256x192.jxl",
        kind="image",
        description="JPEG XL: newest still-image codec in the set.",
        builder=builders.build_jpeg_xl,
        expected={"format": "JXL", "width": 256, "height": 192},
    ),
    Recipe(
        name="images/vector-shapes-300x200.svg",
        kind="image",
        description="Hand-written SVG: vector rasterisation and text.",
        builder=builders.build_svg,
        expected={"format": "SVG", "width": 300, "height": 200},
    ),
    # --- audio -----------------------------------------------------------
    Recipe(
        name="audio/music-3s-44k-mono.wav",
        kind="audio",
        description="Three seconds of violin, uncompressed mono PCM.",
        builder=builders.build_commons_audio,
        options={
            "start_s": 0.5,
            "duration_s": 3,
            "encoder": ["-ac", "1", "-ar", "44100", "-c:a", "pcm_s16le"],
        },
        expected={
            "format": "wav",
            "audio_codec": "pcm_s16le",
            "sample_rate": 44100,
            "channels": 1,
            "duration_s": 3.0,
        },
        source_title=MUSIC,
        source_changes="Trimmed to 3 s, downmixed to mono, 44.1 kHz PCM.",
    ),
    Recipe(
        name="audio/music-3s-tagged.flac",
        kind="audio",
        description="FLAC with Vorbis comments and attached cover art.",
        builder=builders.build_tagged_audio,
        options={
            "start_s": 0.5,
            "duration_s": 3,
            "encoder": ["-c:a", "flac", "-compression_level", "8"],
            "tags": MUSIC_TAGS,
        },
        expected={
            "format": "flac",
            "audio_codec": "flac",
            "duration_s": 3.0,
        },
        source_title=MUSIC,
        source_changes=(
            "Trimmed to 3 s, encoded to FLAC, tagged, cover art embedded."
        ),
    ),
    Recipe(
        name="audio/music-5s-vorbis.ogg",
        kind="audio",
        description="Ogg Vorbis encode of the same excerpt.",
        builder=builders.build_commons_audio,
        options={
            "start_s": 0.5,
            "duration_s": 5,
            "encoder": ["-c:a", "libvorbis", "-q:a", "4"],
        },
        expected={
            "format": "ogg",
            "audio_codec": "vorbis",
            "duration_s": 5.0,
        },
        source_title=MUSIC,
        source_changes="Trimmed to 5 s, re-encoded to Ogg Vorbis q4.",
    ),
    Recipe(
        name="audio/music-5s-mp3-tagged.mp3",
        kind="audio",
        description="MP3 with ID3v2 tags and attached cover art.",
        builder=builders.build_tagged_audio,
        options={
            "start_s": 0.5,
            "duration_s": 5,
            "encoder": [
                "-c:a",
                "libmp3lame",
                "-q:a",
                "4",
                "-id3v2_version",
                "3",
            ],
            "tags": MUSIC_TAGS,
        },
        expected={"format": "mp3", "audio_codec": "mp3", "duration_s": 5.0},
        source_title=MUSIC,
        source_changes=(
            "Trimmed to 5 s, encoded to MP3 q4, tagged, cover art embedded."
        ),
    ),
    Recipe(
        name="audio/music-5s-48k-stereo.opus",
        kind="audio",
        description="Opus at 48 kHz stereo: modern speech and music codec.",
        builder=builders.build_commons_audio,
        options={
            "start_s": 0.5,
            "duration_s": 5,
            "encoder": [
                "-ar",
                "48000",
                "-ac",
                "2",
                "-c:a",
                "libopus",
                "-b:a",
                "64k",
            ],
        },
        expected={
            "format": "ogg",
            "audio_codec": "opus",
            "sample_rate": 48000,
            "channels": 2,
            "duration_s": 5.0,
        },
        source_title=MUSIC,
        source_changes="Trimmed to 5 s, upmixed to stereo, Opus 64 kbit/s.",
    ),
    Recipe(
        name="audio/speech-armstrong-1969.ogg",
        kind="audio",
        description=(
            "Neil Armstrong's first words from the Moon (NASA, 1969), "
            "16 kHz mono. Human speech over a radio link."
        ),
        builder=builders.build_commons_audio,
        options={
            "start_s": 0,
            "duration_s": 8,
            "encoder": [
                "-ac",
                "1",
                "-ar",
                "16000",
                "-c:a",
                "libvorbis",
                "-q:a",
                "3",
            ],
        },
        expected={
            "format": "ogg",
            "audio_codec": "vorbis",
            "sample_rate": 16000,
            "channels": 1,
            "duration_s": 7.699,
        },
        source_title=ARMSTRONG,
        source_changes="Re-encoded to 16 kHz mono Vorbis, no trimming.",
        transcript=ARMSTRONG_TEXT,
    ),
    Recipe(
        name="audio/speech-synthetic-8k.wav",
        kind="audio",
        description=(
            "Synthesized speech at 8 kHz: narrowband telephone audio with "
            "fixed wording."
        ),
        builder=builders.build_synthetic_speech,
        options={"sample_rate": 8000, "channels": 1, "text": SPEECH_TEXT},
        expected={
            "format": "wav",
            "audio_codec": "pcm_s16le",
            "sample_rate": 8000,
            "channels": 1,
            "duration_s_min": 2.0,
        },
        transcript=SPEECH_TEXT,
    ),
    # --- video -----------------------------------------------------------
    Recipe(
        name="video/testsrc-2s-h264-aac.mp4",
        kind="video",
        description="Two-second test pattern with a 440 Hz tone, H.264/AAC.",
        builder=builders.build_synthetic_clip,
        options={
            "size": "320x240",
            "rate": 25,
            "duration_s": 2,
            "encoder": [
                "-c:v",
                "libx264",
                "-crf",
                "28",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-b:a",
                "64k",
                "-movflags",
                "+faststart",
            ],
        },
        expected={
            "format": "mov,mp4,m4a,3gp,3g2,mj2",
            "video_codec": "h264",
            "audio_codec": "aac",
            "width": 320,
            "height": 240,
            "audio_tracks": 1,
            "duration_s": 2.0,
        },
    ),
    Recipe(
        name="video/testsrc-2s-vp9-opus.webm",
        kind="video",
        description="Same pattern as WebM with VP9 video and Opus audio.",
        builder=builders.build_synthetic_clip,
        options={
            "size": "320x240",
            "rate": 25,
            "duration_s": 2,
            "encoder": [
                "-c:v",
                "libvpx-vp9",
                "-crf",
                "40",
                "-b:v",
                "0",
                "-c:a",
                "libopus",
                "-b:a",
                "64k",
            ],
        },
        expected={
            "format": "matroska,webm",
            "video_codec": "vp9",
            "audio_codec": "opus",
            "width": 320,
            "height": 240,
            "audio_tracks": 1,
            "duration_s": 2.0,
        },
    ),
    Recipe(
        name="video/testsrc-3s-silent.mp4",
        kind="video",
        description="Video with no audio stream at all: stream-count mismatch.",
        builder=builders.build_silent_clip,
        options={
            "size": "320x240",
            "rate": 25,
            "duration_s": 3,
            "encoder": [
                "-c:v",
                "libx264",
                "-crf",
                "28",
                "-pix_fmt",
                "yuv420p",
            ],
        },
        expected={
            "format": "mov,mp4,m4a,3gp,3g2,mj2",
            "video_codec": "h264",
            "width": 320,
            "height": 240,
            "audio_tracks": 0,
            "duration_s": 3.0,
        },
    ),
    Recipe(
        name="video/counter-5s-h264.mp4",
        kind="video",
        description=(
            "Five seconds with the frame number and timestamp burned in: "
            "frame extraction and seeking can be checked by eye."
        ),
        builder=builders.build_counter_clip,
        options={
            "size": "480x270",
            "rate": 25,
            "duration_s": 5,
            "encoder": [
                "-c:v",
                "libx264",
                "-crf",
                "28",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-b:a",
                "64k",
            ],
        },
        expected={
            "video_codec": "h264",
            "audio_codec": "aac",
            "width": 480,
            "height": 270,
            "duration_s": 5.0,
        },
    ),
    Recipe(
        name="video/nasa-pia10149-4s.mp4",
        kind="video",
        description=(
            "Four seconds of the NASA/JPL PIA10149 animation: Europa in "
            "cutaway view orbiting Jupiter. Rendered imagery without audio, "
            "for encoding tests."
        ),
        builder=builders.build_commons_clip,
        options={
            "start_s": 0,
            "duration_s": 4,
            "width": 640,
            "encoder": [
                "-c:v",
                "libx264",
                "-crf",
                "30",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-b:a",
                "64k",
                "-movflags",
                "+faststart",
            ],
        },
        expected={
            "format": "mov,mp4,m4a,3gp,3g2,mj2",
            "video_codec": "h264",
            "width": 640,
            "duration_s": 4.0,
        },
        source_title=MARS,
        source_changes="Trimmed to 4 s, scaled to 640 px, re-encoded to H.264.",
    ),
    Recipe(
        name="video/sarychev-eruption-4s.webm",
        kind="video",
        description=(
            "Four seconds of the 2009 Sarychev Peak eruption seen from the "
            "ISS: real footage without audio."
        ),
        builder=builders.build_commons_clip,
        options={
            "start_s": 0,
            "duration_s": 4,
            "width": 480,
            "encoder": ["-c:v", "libvpx-vp9", "-crf", "42", "-b:v", "0", "-an"],
        },
        expected={
            "format": "matroska,webm",
            "video_codec": "vp9",
            "width": 480,
            "audio_tracks": 0,
            "duration_s": 4.0,
        },
        source_title=ERUPTION,
        source_changes="Trimmed to 4 s, scaled to 480 px, re-encoded to VP9.",
    ),
    Recipe(
        name="video/speaking-cdc-interview-6s.mp4",
        kind="video",
        description=(
            "First six seconds of a CDC staff interview: a person talking "
            "to camera, for speech and face detection. The source page "
            "quotes the opening words."
        ),
        builder=builders.build_commons_clip,
        options={
            "start_s": 0,
            "duration_s": 6,
            "width": 640,
            "encoder": [
                "-c:v",
                "libx264",
                "-crf",
                "30",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-b:a",
                "64k",
                "-movflags",
                "+faststart",
            ],
        },
        expected={
            "format": "mov,mp4,m4a,3gp,3g2,mj2",
            "video_codec": "h264",
            "audio_codec": "aac",
            "width": 640,
            "audio_tracks": 1,
            "duration_s": 6.0,
        },
        source_title=CDC,
        source_changes=(
            "Trimmed to the first 6 s, scaled to 640 px, re-encoded to "
            "H.264/AAC."
        ),
        transcript=CDC_TEXT,
    ),
    Recipe(
        name="video/multitrack-2audio-1subtitle.mkv",
        kind="video",
        description=(
            "Matroska with two audio tracks (tagged eng and jpn) and one "
            "subtitle track: track selection and metadata."
        ),
        builder=builders.build_multitrack_mkv,
        expected={
            "format": "matroska,webm",
            "video_codec": "h264",
            "audio_codec": "opus",
            "audio_tracks": 2,
            "subtitle_tracks": 1,
            "width": 320,
            "height": 240,
            "duration_s": 4.0,
        },
    ),
    Recipe(
        name="video/subtitles-2cues.srt",
        kind="text",
        description="Two-cue SubRip subtitle file.",
        builder=builders.build_subtitles,
        options={"format": "srt"},
        expected={"lines": 7},
        transcript="First cue line.\nSecond cue line.",
    ),
    Recipe(
        name="video/subtitles-2cues.vtt",
        kind="text",
        description="The same two cues as WebVTT.",
        builder=builders.build_subtitles,
        options={"format": "vtt"},
        expected={"lines": 7},
        transcript="First cue line.\nSecond cue line.",
    ),
    # --- text ------------------------------------------------------------
    Recipe(
        name="text/unicode-torture.txt",
        kind="text",
        description=(
            "One line per Unicode class: CJK, emoji, RTL, combining marks, "
            "zero-width characters, fullwidth forms."
        ),
        builder=builders.build_unicode_torture,
        expected={"lines": 11, "bytes_min": 400},
    ),
    Recipe(
        name="text/unicode-torture-bom.txt",
        kind="text",
        description="The Unicode torture lines behind a UTF-8 byte order mark.",
        builder=builders.build_unicode_torture,
        options={"bom": True},
        expected={"lines": 11},
    ),
    Recipe(
        name="text/crlf-lines.txt",
        kind="text",
        description="CRLF line endings: Windows text handling.",
        builder=builders.build_crlf,
        expected={"lines": 3},
    ),
    Recipe(
        name="text/no-final-newline.txt",
        kind="text",
        description="Last line has no terminator: line-reader behaviour.",
        builder=builders.build_no_final_newline,
        expected={"lines": 2},
    ),
    Recipe(
        name="text/latin1-bytes.txt",
        kind="text",
        description="Latin-1 bytes, not valid UTF-8: encoding detection.",
        builder=builders.build_latin1,
        expected={"lines": 1},
    ),
    Recipe(
        name="text/nul-bytes.txt",
        kind="text",
        description="Embedded NUL bytes: breaks naive line handling.",
        builder=builders.build_nul_bytes,
        expected={"lines": 2},
    ),
    Recipe(
        name="text/long-line-100k.txt",
        kind="text",
        description="One 100000-byte line: buffer and wrapping limits.",
        builder=builders.build_long_line,
        expected={"lines": 1, "bytes": 100_001},
    ),
    # --- odd filesystem cases -------------------------------------------
    Recipe(
        name="odd/name with spaces.png",
        kind="image",
        description="Small PNG whose name contains spaces.",
        builder=builders.build_plain_png,
        options={"size": "32x32"},
        expected={"format": "PNG", "width": 32, "height": 32},
    ),
    Recipe(
        name="odd/-dash-prefixed.png",
        kind="image",
        description="Name starting with a dash: argument parsing trap.",
        builder=builders.build_plain_png,
        options={"size": "40x24"},
        expected={"format": "PNG", "width": 40, "height": 24},
    ),
    Recipe(
        name="odd/имя-кириллица.txt",
        kind="text",
        description="Cyrillic file name: non-ASCII path handling.",
        builder=builders.build_odd_text,
        expected={"lines": 1},
    ),
    Recipe(
        name="odd/emoji-🎬-clapper.txt",
        kind="text",
        description="File name with an emoji outside the basic plane.",
        builder=builders.build_odd_text,
        expected={"lines": 1},
    ),
    Recipe(
        name="odd/png-content-named-jpg.jpg",
        kind="image",
        description="PNG bytes behind a .jpg extension: sniffing by content.",
        builder=builders.build_png_named_jpg,
        expected={"format": "PNG", "width": 48, "height": 48},
    ),
    Recipe(
        name="odd/truncated-jpeg.jpg",
        kind="text",
        description="First 2048 bytes of a JPEG: damaged input handling.",
        builder=builders.build_truncated_jpeg,
        expected={"bytes": 2048},
    ),
    Recipe(
        name="odd/zero-bytes.bin",
        kind="text",
        description="Empty file: the degenerate input.",
        builder=builders.build_zero_bytes,
        expected={"bytes": 0, "lines": 0},
    ),
    Recipe(
        name="odd/no-extension",
        kind="image",
        description="JPEG bytes with no extension: content detection alone.",
        builder=builders.build_no_extension,
        expected={"format": "JPEG", "width": 120, "height": 80},
    ),
    Recipe(
        name="odd/dir with spaces/inner.txt",
        kind="text",
        description="Directory name with spaces.",
        builder=builders.build_odd_text,
        expected={"lines": 1},
    ),
)
