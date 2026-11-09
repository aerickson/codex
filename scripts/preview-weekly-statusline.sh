#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root/codex-rs"

printf '%s\n\n' 'Weekly quota statusline preview (live renderer, no API calls)'

just test -p codex-tui status_line_preview_script --no-capture 2>&1 \
  | awk '
      /STATUSLINE_PREVIEW_NON_GROUPED_BEGIN/ {
        print "Non-grouped:"
        section = "non-grouped"
        next
      }
      /STATUSLINE_PREVIEW_NON_GROUPED_END/ {
        print ""
        section = ""
        next
      }
      /STATUSLINE_PREVIEW_GROUPED_BEGIN/ {
        print "Grouped:"
        section = "grouped"
        next
      }
      /STATUSLINE_PREVIEW_GROUPED_END/ {
        print ""
        section = ""
        next
      }
      section != "" {
        print "  " $0
      }
    '

cat <<'EOF'
Items:
  five-hour-limit
  five-hour-limit-reset-in
  weekly-limit
  weekly-limit-reset-in
  weekly-limit-runway       (legacy alias: wquota-runway)
  weekly-limit-margin       (legacy alias: weekly-reset-margin)
EOF
