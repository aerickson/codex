#!/usr/bin/env python3
"""Display local deployment metadata and changes since each build."""

from __future__ import annotations

import datetime
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


def run(*args: str) -> str:
    result = subprocess.run(args, capture_output=True, text=True, check=False)
    return result.stdout.strip()


def git_commit_for_build(version: str) -> str | None:
    match = re.search(r"\+([0-9a-f]{8,40})$", version)
    if match is None:
        return None
    commit = match.group(1)
    result = subprocess.run(
        ["git", "rev-parse", "--verify", f"{commit}^{{commit}}"],
        capture_output=True,
        text=True,
        check=False,
    )
    return commit if result.returncode == 0 else None


def signing_details(binary: Path) -> str:
    codesign = shutil.which("codesign")
    if codesign is None:
        return "signing: unavailable (codesign not found)"

    result = subprocess.run(
        [codesign, "-dv", "--verbose=4", str(binary)],
        capture_output=True,
        text=True,
        check=False,
    )
    details = {}
    for line in result.stderr.splitlines() + result.stdout.splitlines():
        key, separator, value = line.partition("=")
        if separator:
            details[key] = value

    if "Signature size" not in details:
        return "signing: unsigned"

    return (
        "signing: signed"
        f"  identity: {details.get('Authority', '-')}"
        f"  team: {details.get('TeamIdentifier', '-')}"
        f"  cdhash: {details.get('CDHash', '-')}"
    )


def main() -> int:
    home = Path.home()
    deployments = {
        "staged": home / "bin" / "codex-aje-next",
        "active": home / "bin" / "codex-aje",
    }
    use_color = sys.stdout.isatty()
    bold = "\033[1m" if use_color else ""
    cyan = "\033[36m" if use_color else ""
    green = "\033[32m" if use_color else ""
    yellow = "\033[33m" if use_color else ""
    reset = "\033[0m" if use_color else ""

    head_commit = run("git", "rev-parse", "--verify", "HEAD")
    print(
        f"{bold}Deployment{reset:<10}  {'Binary':<18}  {'Version':<32}  "
        f"{'Checksum':<10}  Modified"
    )
    print(f"{'-' * 10}  {'-' * 18}  {'-' * 32}  {'-' * 10}  {'-' * 19}")

    for name, binary in deployments.items():
        if not binary.is_file() or not os.access(binary, os.X_OK):
            print(f"{yellow}{name:<10}{reset}  {binary.name:<18}  {yellow}missing{reset}")
            continue

        version = run(str(binary), "--version")
        checksum = run("cksum", str(binary)).split(maxsplit=1)[0]
        modified = datetime.datetime.fromtimestamp(
            binary.stat().st_mtime,
            datetime.datetime.now().astimezone().tzinfo,
        ).strftime("%Y-%m-%d %H:%M:%S %z")
        print(
            f"{cyan}{name:<10}{reset}  {binary.name:<18}  {version:<32}  "
            f"{checksum:<10}  {modified}"
        )

        build_commit = git_commit_for_build(version)
        if build_commit and head_commit:
            commit_count = run("git", "rev-list", "--count", f"{build_commit}..{head_commit}")
            print(
                f"  built commit: {build_commit:<12}  commits since build: {commit_count:<4}"
                f"  git diff: {build_commit}..HEAD"
            )
        else:
            print(
                f"  built commit: {(build_commit or 'unknown'):<12}  commits since build: -"
                "     git diff: unavailable"
            )
        print(f"  {signing_details(binary)}")

    staged = deployments["staged"]
    active = deployments["active"]
    if staged.is_file() and active.is_file():
        if staged.read_bytes() == active.read_bytes():
            print(f"{green}✓ identical{reset}  staged and active binaries match")
        else:
            print(f"{yellow}✗ different{reset}  staged and active binaries differ")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
