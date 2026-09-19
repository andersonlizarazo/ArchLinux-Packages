# media-fixtures-strings

The Big List of Naughty Strings, packaged as test input for programs that
handle user-supplied text.

The list contains strings with a high probability of breaking input handling:
reserved words, numeric strings, format strings, command injection, SQL
injection, path traversal, terminal escape sequences, Unicode, right-to-left
text, combining marks, and very long strings.

## Files

| File | Meaning |
| --- | --- |
| `blns.txt` | The list, one string per line, with comments |
| `blns.json` | The same list as a JSON array |
| `LICENSE` | Upstream MIT licence |
| `upstream.json` | Repository, commit, and the SHA-256 of every file |

Upstream publishes no tagged releases, so `upstream.json` pins the commit
`db33ec7b1d5d9616a88c76394b7d0897bd0b97eb` (2021-04-17).

Upstream: <https://github.com/minimaxir/big-list-of-naughty-strings>

## Refresh

    python3 tools/fetch_blns.py

The script downloads the pinned commit and fails if any checksum differs from
`upstream.json`. Delete `upstream.json` only when intentionally moving to a
newer commit; the script then resolves the current commit of the default
branch and writes a new pin.

## Licence

MIT. The upstream licence text ships as `LICENSE`.
