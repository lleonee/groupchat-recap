# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased] - 2026-10-18

### Added
- **Analysis period selector** on the home page: "All Time" (default) or "Sadece 2026". Switching re-runs the analysis on the loaded chat.

### Changed
- **Fullscreen presentation is the main result**: the JS (Chart.js) slide deck now opens directly in fullscreen after analysis and sits above the name editor. Added an "✏️ İsimler" button and Esc to exit fullscreen.

### Fixed
- WhatsApp placeholders between `<` and `>` ("<görsel dahil edilmedi>", "<album mesajı>", "<GIF dahil edilmedi>", "<Bu mesaj düzenlendi.>") are removed; media-only messages are ignored entirely.
- Dates from English-language phone exports (`MM/DD/YY`) were read as day/month, rolling invalid months into later years (messages showing up in 2027-2028). The date order is now detected per chat and impossible dates are rejected; 2-digit years are handled for both `.` and `/` formats.
- Title slide now lists every member instead of only the top 6.
- "Meta AI" (WhatsApp bot) is ignored in all statistics and the name list.
- Calmer, consistent closing slide (no duplicated red all-caps title).
- Slide PDF pages were shifted down (white band on top) when the page was scrolled during export.
- Monthly activity chart had hard-coded "Aralık '24 – Kasım '25" labels; it now covers the real months of the chat (with years when it spans several).
- Links (`https://…`, `www.…`, `site.com/…`) are stripped from messages before word, character, emoji, caps and profanity analysis.
- "📥 Slayt PDF" export produced a single blank page; it now renders every slide as its own PDF page.

### Removed
- **Python/PyScript PDF generator** (`pdf_worker.py`, `stats_logic.py`, `worker_config.json`): no more Pyodide/pandas/matplotlib download. PDFs are still available via the JS "📥 Slayt PDF" export.

### Security
- Chat-derived text (group name, contact names, words, emojis) is now HTML-escaped before rendering, so a crafted name can't inject markup or trigger network requests.
- Added a Content-Security-Policy with `connect-src 'none'`, so the browser blocks any outgoing data request.
- Pinned Chart.js to 4.5.1 and added Subresource Integrity hashes to all CDN scripts.

## [2025-12-12]

### Added
- **Base64 Obfuscation**: Protected the profanity blacklist in `recap_logic.py` using Base64 encoding to prevent casual viewing in the repository.
- **Enhanced Blacklist**: Merged `blacklist.xlsx` (~4778 words) into the core filter for better coverage.
- **CHANGELOG.md**: Started tracking project updates.

### Changed
- Refactored `recap_logic.py` to decode blacklist at runtime (Zero performance cost).
- Cleaned up development files (`yearly_recap.py`, etc.).
- Fixed `index.html` banner image reference (`jpg` -> `png`).
- Localized title tags and stripped console logs for production.
