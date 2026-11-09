#!/usr/bin/env python3
"""Run a build with its commit identity and a reachable release baseline."""

import os
import re
import subprocess
import sys


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: local_build_version.py COMMAND [ARG ...]")
    sha = git("rev-parse", "--short=12", "HEAD")
    dirty = bool(git("status", "--porcelain", "--untracked-files=no"))
    version = f"0.0.0+g{sha}{'.dirty' if dirty else ''}"
    tags = git("tag", "--merged", "HEAD", "--list", "rust-v*", "--sort=-version:refname")
    baseline = next(
        (tag[6:] for tag in tags.splitlines()
         if re.fullmatch(r"rust-v(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)", tag)
         and not tag.startswith("rust-v0.0.")),
        "",
    )
    os.environ.update(CODEX_AJE_VERSION=version, CODEX_BUILD_VERSION=version,
                      CODEX_AJE_RELEASE_BASELINE=baseline)
    os.execvp(sys.argv[1], sys.argv[1:])


if __name__ == "__main__":
    main()
