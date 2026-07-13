# Branch summary

Branch: `20260710-status-line-rate-limit-reset-countdowns`

Commit: `e9e96974a9`

This branch adds quota-reset countdowns and a weekly quota runway estimate to the Codex TUI
status line. It uses the existing `account/rateLimits/read` data path and retains each window's
absolute reset timestamp so countdowns can update as time passes without another API response.
Weekly quota percentage, reset countdown, and runway items merge when configured adjacently.

## Configuration

The rate-limit `tui.status_line` items are:

- `five-hour-limit` (existing)
- `weekly-limit` (existing)

- `five-hour-limit-reset-in` (new)
- `weekly-limit-reset-in` (new)
- `weekly-limit-runway` (new; estimated time until the weekly quota is exhausted at the current usage rate)
- `weekly-limit-margin` (new; signed difference between projected exhaustion and reset time)

The legacy `wquota-runway` identifier remains accepted as an alias for `weekly-limit-runway`.

When a reset item immediately follows its matching percentage item, the two indicators are
rendered as one segment. When the weekly runway immediately follows that pair, it is included in
the same segment. The items remain independently configurable, so each can still be shown alone.
For example:

```toml
[tui]
status_line = [
  "five-hour-limit",
  "five-hour-limit-reset-in",
  "weekly-limit",
  "weekly-limit-reset-in",
  "weekly-limit-runway",
  "weekly-limit-margin",
]
```

V1 rendered the indicators as separate segments:

```text
5h 53% left · 5h reset 1h 42m · weekly 93% left · Week reset 3d 8h · WQuota runway: ~18h
```

V2 merges each reset countdown into its matching percentage item:

```text
5h 53% left (reset 1h 42m) · weekly 93% left (reset 3d 8h; runway ~18h; margin -2d 14h)
```

When shown alone, the runway is labeled `weekly runway: ~18h` and the margin is labeled
`reset margin: -2d 14h`.

Missing or expired reset timestamps omit the corresponding countdown item. Countdown redraws are
scheduled at minute boundaries. The runway is shown as `n/a` when the weekly window or a
meaningful usage rate is unavailable.

## Validation

- `just test -p codex-tui`: targeted statusline merge test passed.
- `just fix -p codex-tui` passed.
- Release CLI build completed from this branch.
