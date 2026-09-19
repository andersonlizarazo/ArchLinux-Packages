# pkgbuild

`PKGBUILD` files for the packages in this repository. Each one fetches a tagged
archive of the repository and installs files from the matching `package/<name>/`
directory. Nothing is generated at package build time.

| Package | Source directory | Installed |
| --- | --- | --- |
| `media-fixtures` | `package/media-fixtures/` | Fixtures, manifest, checksums, attribution, transcripts, license |
| `media-fixtures-strings` | `package/media-fixtures-strings/` | `blns.txt` and `blns.json` |
| `media-fixtures-root` | none | Symlink `/media-fixtures` and two short fixture names |

## Build

    cd pkgbuild/<name>
    updpkgsums
    makepkg -f
    namcap PKGBUILD
    namcap ./*.pkg.tar.zst
    makepkg --printsrcinfo > .SRCINFO

`media-fixtures-strings` and `media-fixtures-root` depend on `media-fixtures`.
Building them on a system without that package installed needs
`makepkg -f --nodeps`.

## Source resolution

Every recipe fetches
`https://github.com/andersonlizarazo/ArchLinux-Packages/archive/refs/tags/v$pkgver.tar.gz`,
which unpacks to `ArchLinux-Packages-$pkgver/`.

`makepkg` rejects a `source=` entry containing `../`, so a build before a tag
exists needs the archive in the recipe directory under the exact
`$pkgname-$pkgver.tar.gz` name. `makepkg` then uses the local file and still
checks `sha256sums`.

`makepkg` reuses a `*.tar.gz` that is already in the recipe directory instead of
downloading it again, so an old download has to be deleted before running
`updpkgsums` after the source changes.

## Installed layout

`media-fixtures` installs the fixture directories directly into the data
directory, so a fixture is `/media-fixtures/audio/speech-synthetic-8k.wav`, not
`/media-fixtures/fixtures/audio/...`. The manifest, the checksums, the
transcripts and the attribution sit beside them.

## Short fixture names

`media-fixtures-root` adds a name for each fixture whose own name does not
describe the photo:

| Installed path | Target |
| --- | --- |
| `/media-fixtures/woman-with-cat.jpg` | `images/photo-cat-1995.jpg` |
| `/media-fixtures/yellow-poppies.jpg` | `images/photo-poppy-red-hills-2016.jpg` |

The targets are relative, so the links resolve inside the installed tree.

## Verification

`check()` cannot verify the installed tree: `makepkg` runs `check()` before
`package()`, when `$pkgdir` is still empty. `media-fixtures` therefore runs
`sha256sum -c ../checksums.txt` at the end of `package()`, which checks the
bytes that ship.

## Expected namcap findings

| Finding | Reason |
| --- | --- |
| `media-fixtures` reports a file name with non standard characters | `fixtures/odd/` tests non-ASCII file names on purpose |
| `media-fixtures-root` reports a file in a non-standard directory | The package installs one root-level symlink by design |
| `media-fixtures-root` reports symlinks pointing to non-existing paths | Every target comes from the `media-fixtures` dependency, which namcap does not follow |
| Both dependent packages report an unnecessary dependency | Both install into the tree owned by `media-fixtures` |

## ShellCheck

`PKGBUILD` is read by bash, and the metadata arrays require bash, so the POSIX
shell rule used elsewhere in this repository cannot apply here. Each file starts
with `# shellcheck disable=SC2034,SC2154`: `makepkg` assigns `srcdir` and
`pkgdir`, and reads the metadata variables itself.

    shfmt -ln=bash -i 2 -d pkgbuild/*/PKGBUILD
    shellcheck -s bash pkgbuild/*/PKGBUILD
