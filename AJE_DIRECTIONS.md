# AJE local directions

This file is intentionally unversioned and is for local deployment notes.

## Build and validation

From the repository root:

```sh
nice -n 10 just --justfile justfile.aje build
just --justfile justfile.aje test -p codex-tui
```

The resulting binary is:

```text
codex-rs/target/release/codex
```

## Local deployment

Stage the validated release binary with:

```sh
just --justfile justfile.aje deploy-next
```

This copies the binary to `~/bin/codex-aje-next` using an atomic rename so macOS does not reuse
the previous executable's signature state. After additional validation, promote it with:

```sh
just --justfile justfile.aje promote-next
```

New builds should always go to `codex-aje-next` first. Do not promote it until the staged binary
has been tested and is ready for release.
