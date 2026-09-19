# Pre-commit hook

Runs the repository's formatter, linters, and fast tests in verification mode.
It never rewrites files: fix what it reports, then commit again.

Checks: `ruff format --check`, `ruff check`, `pytest` over the fixture tools,
`shfmt` and `shellcheck` over the hook and the `PKGBUILD` files, and a grep for
leftover `!D: ` debug prints.

## Install

    git config core.hooksPath scripts

## Uninstall

    git config --unset core.hooksPath
