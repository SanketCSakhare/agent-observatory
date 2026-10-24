# Verification record

Authoring date: 24 October 2026.

## Completed

- 15 Python standard-library unittest checks pass: deterministic simulation, SQL/source reconciliation, retry denominators, duplicate/orphan/missing-sequence handling, negative durations, outcome/time/attempt consistency, transaction rollback, safe JSON embedding, globally unique call ownership, executable SQL and empty input.
- Node.js logic harness passes: six view render functions, expected default KPIs, retry recovery counts, combined task/version filtering, no-results message, reset, trace content, HTML escaping and percentile calculation.
- Default pipeline rebuilt successfully with 1,200 sessions and 9,412 events.
- Deterministic rebuild checked against versioned outputs.

## Limits

The JavaScript harness supplies a minimal document stub. It is not a rendering engine. Browser binaries were absent and the Chromium installation download failed. Therefore screenshots, actual click/focus behaviour, downloaded CSV bytes, responsive layout and assistive-technology behaviour were not verified. No screenshots are included and none are represented as real renders.

GitHub CI is authored but has not run remotely. The project is published in the agent-observatory GitHub repository. Runtime has no third-party dependencies; Node is used for development checks only.

## Browser acceptance checklist for a reviewer

1. Open `dashboard/index.html` in Chrome, Firefox or Edge; check for console errors.
2. Confirm 1,200 sessions, 97.1% technical success and 84.3% user completion with default filters.
3. Open each of six sections. Apply task and version filters, then a date range with no data; reset.
4. Select multiple session traces and inspect an API failure followed by retry.
5. Download CSV, verify the header and that its row count matches the filtered session count.
6. Check desktop and 390-pixel mobile widths for clipping; use keyboard navigation and visible focus.

Do not replace this limitation with a claim of browser testing until those checks have actually run.
