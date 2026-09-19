# media-fixtures

Small media and text files with properties that are documented and checked
against the files themselves. The set exists so that software which reads
images, audio, video or text can be exercised without downloading anything
first, and so that a test can assert on real numbers instead of on what a file
is assumed to contain.

Properties are measured with `ffprobe` and ImageMagick `identify`, never
copied from a specification.

## Contents

| Directory | What it covers |
| --- | --- |
| `fixtures/images/` | Photographs (Giza pyramids 1904, a portrait, a cat, a poppy, an 1847 lithograph), JPEG, PNG, 16-bit grayscale, palette PNG, alpha, GIF and APNG animation, multi-page TIFF, CMYK JPEG, WebP (lossy and alpha), AVIF, JPEG XL, SVG, a 4000x3000 JPEG, a 1x1 pixel, rendered text at six point sizes |
| `fixtures/audio/` | WAV, FLAC, Ogg Vorbis, MP3, Opus; mono and stereo; 8 kHz, 16 kHz, 44.1 kHz and 48 kHz; ID3 and Vorbis tags; embedded cover art; Neil Armstrong's 1969 Moon line; synthesized speech |
| `fixtures/video/` | H.264/AAC in MP4, VP9/Opus in WebM, a clip with no audio stream, Matroska with two audio tracks and one subtitle track, a burned-in frame counter, real footage, a person speaking to camera |
| `fixtures/text/` | UTF-8 torture lines, a byte order mark, CRLF, a missing final newline, Latin-1 bytes, embedded NUL bytes, a 100000-byte line |
| `fixtures/odd/` | Names with spaces, a leading dash, Cyrillic and emoji; PNG content in a `.jpg`; a truncated JPEG; an empty file; a file with no extension; a directory with spaces |

Total size is about 2 MiB.

## Documented properties

| File | Meaning |
| --- | --- |
| `manifest.json` | Machine-readable record: path, kind, description, measured properties, byte size, SHA-256, and the source of downloaded files |
| `EXPECTED.md` | The same inventory as a table |
| `checksums.txt` | `sha256sum -c` compatible list |
| `ATTRIBUTION.md` | What each downloaded file shows, who made it, its license, and the changes made to it |
| `TRANSCRIPTS.md` | The exact words carried by the speech, subtitle and rendered-text fixtures |

## Verify

    cd package/media-fixtures
    python3 tools/generate.py --verify

Verification re-measures every file and fails when a file, its checksum, or any
recorded property changed. It writes nothing.

## List

    python3 tools/generate.py --list

## Regenerate

Regeneration rewrites `fixtures/` and every report file. It needs `python3`,
`ffmpeg`, ImageMagick and `espeak-ng`, and it downloads about 13 MiB from
Wikimedia Commons into `cache/`, which is not tracked by Git.

    python3 tools/generate.py
    python3 tools/generate.py --refresh-sources   # re-pin the downloads

Regeneration is byte-reproducible: the same inputs produce the same files, so
a rerun leaves the working tree unchanged. The options that make that true
(fixed random seed, no PNG date chunks, no encoder timestamps or random stream
identifiers) are injected in `tools/media.py` instead of being repeated in
every builder.

## Add a fixture

1. Add a builder function to `tools/builders.py`.
2. Add a `Recipe` to `tools/recipes.py` declaring what the file must measure.
3. Run `python3 tools/generate.py`.

A declaration that does not match the produced file fails the run, so the
manifest cannot claim something the file does not have.

## Licensing

Files produced by `tools/` are released under CC0-1.0; see `LICENSE`.

Files listed in `ATTRIBUTION.md` come from public domain material on Wikimedia
Commons. Public domain works carry no attribution requirement; author, source
and the changes made are recorded anyway.

## Deliberate omissions

- A file name containing a newline: it breaks the line-oriented format that
  `sha256sum -c` reads.
- Multi-gigabyte video and raw camera formats: the size budget matters more
  than the coverage.
