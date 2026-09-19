# ArchLinux-Packages

Arch Linux package recipes and the source they package. A general home for
packages built for one Arch Linux installation; nothing here is tied to a
single application.

## Layout

| Directory | Contents |
| --- | --- |
| `package/<name>/` | Source authored here: generators, inputs, and pinned upstream files |
| `pkgbuild/<name>/` | `PKGBUILD` for `package/<name>`, fetching it from this repository |

A package that only installs files already provided by another package keeps its
`PKGBUILD` under `pkgbuild/` and needs no `package/` directory.

## Packages

| Package | Source | Purpose |
| --- | --- | --- |
| `media-fixtures` | `package/media-fixtures/` | Sample media and text files with documented, checked properties, for testing software |
| `media-fixtures-strings` | `package/media-fixtures-strings/` | Strings that commonly break programs (Big List of Naughty Strings) |
| `media-fixtures-root` | `pkgbuild/media-fixtures-root/` | Convenience symlink `/media-fixtures` for `media-fixtures`, plus two short fixture names |

`media-fixtures-strings` installs into the tree owned by `media-fixtures`, so
it depends on it. Each package documents itself in the `README.md` beside its
source.

## Adding a package

1. Author the source under `package/<name>/`, recording the version in it.
2. Add `pkgbuild/<name>/PKGBUILD` with a source that fetches the archive of the
   matching tag, for example:

       source=("$pkgname-$pkgver.tar.gz::https://github.com/andersonlizarazo/ArchLinux-Packages/archive/refs/tags/v$pkgver.tar.gz")

3. Tag the release `v<version>` so that archive URL resolves, then run
   `updpkgsums` and `makepkg --printsrcinfo > .SRCINFO`.

## Status

The `media-fixtures` and `media-fixtures-strings` sources are complete, and the
`pkgbuild/` recipes build all three packages against the `v1.0.0` tag. Build
commands are in `pkgbuild/README.md`.

## AI usage

AI assistance was used, in the form of a coding agent under human supervision,
to write the package sources, their generators and verification tools, and this
documentation. Generated files, such as the fixture set and its manifest, are
produced by running the tools under `package/*/tools/`, and every documented
property is measured from the file that ships.
