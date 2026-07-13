# Branch summary

Branch: `20260710-status-line-rate-limit-reset-countdowns`

Commit: `718950d9c4`

This branch adds quota-reset countdowns and a weekly quota runway estimate to the Codex TUI
status line. It uses the existing `account/rateLimits/read` data path and retains each window's
absolute reset timestamp so countdowns can update as time passes without another API response.

## Configuration

The rate-limit `tui.status_line` items are:

- `five-hour-limit` (existing)
- `weekly-limit` (existing)

- `five-hour-limit-reset-in` (new)
- `weekly-limit-reset-in` (new)
- `wquota-runway` (new; estimated time until the weekly quota is exhausted at the current usage rate)

When a reset item immediately follows its matching percentage item, the two indicators are
rendered as one segment. They remain independently configurable, so either can still be shown
alone. For example:

```toml
[tui]
status_line = [
  "five-hour-limit",
  "five-hour-limit-reset-in",
  "weekly-limit",
  "weekly-limit-reset-in",
  "wquota-runway",
]
```

V1 rendered the indicators as separate segments:

```text
5h 53% left · 5h reset 1h 42m · weekly 93% left · Week reset 3d 8h · WQuota runway: ~18h
```

V2 merges each reset countdown into its matching percentage item:

```text
5h 53% left (reset 1h 42m) · weekly 93% left (reset 3d 8h) · WQuota runway: ~18h
```

Missing or expired reset timestamps omit the corresponding countdown item. Countdown redraws are
scheduled at minute boundaries. The runway is shown as `n/a` when the weekly window or a
meaningful usage rate is unavailable.

## Validation

- `just test -p codex-tui`: 2,981 tests passed, 4 skipped.
- `just fix -p codex-tui` passed.
- Release CLI build completed from this branch.
