#!/usr/bin/env python3
"""Run a local Cargo command with the checkout's matching V8 artifacts."""

import os
from pathlib import Path
import subprocess
import sys

os.environ["CODEX_REPO_ROOT"] = str(Path(__file__).resolve().parent.parent)

from codex_package.targets import TARGET_SPECS
from codex_package.v8 import resolve_codex_v8_cargo_env


def main() -> None:
    args = sys.argv[1:]
    if not args:
        raise SystemExit("Usage: local_v8.py COMMAND [ARG ...]")

    target = os.environ.get("CARGO_BUILD_TARGET")
    for index, arg in enumerate(args):
        if arg == "--target" and index + 1 < len(args):
            target = args[index + 1]
        elif arg.startswith("--target="):
            target = arg.partition("=")[2]
    if not target:
        rustc = os.environ.get("RUSTC", "rustc")
        version = subprocess.check_output([rustc, "-vV"], text=True)
        target = next(line.removeprefix("host: ") for line in version.splitlines() if line.startswith("host: "))

    try:
        spec = TARGET_SPECS[target]
    except KeyError:
        raise SystemExit(f"Unsupported V8 target: {target}") from None
    os.environ.update(resolve_codex_v8_cargo_env(spec))
    os.execvp(args[0], args)


if __name__ == "__main__":
    main()
