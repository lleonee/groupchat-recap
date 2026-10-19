# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased] - 2026-10-18

### Added
- **"✨ Örnek sunum oluştur"** button: builds a fictional but realistic group chat in the browser (6 friends, ~20 months, ~16k messages) and opens its deck, so the site can be tried without uploading a chat.
- **"🔒 Gizlilik Hakkında"** section on the home page: explains that the chat never leaves the device and is processed in the browser, and how to download the code from GitHub and run it locally.
- Swipe left/right on the slide to change slides on touch screens.
- **Analysis period selector** on the home page: "All Time" (default) or "Sadece 2026". Switching re-runs the analysis on the loaded chat.

### Changed
- Footer reads "Made By Leon Efe Apaydın".
- **Fullscreen presentation is the main result**: the JS (Chart.js) slide deck now opens directly in fullscreen after analysis and sits above the name editor. Added an "✏️ İsimler" button and Esc to exit fullscreen.

### Fixed
- "Gece Kuşu" showed each person's own night ratio while the slide and methodology describe the share of the group's 00:00-05:00 messages; it now uses the share, like "Sabah Kuşu".
- DM "Sohbeti X taşıyor" named the alphabetically first person instead of the one who sends more.
- Group top-word slides now skip conjunctions/stopwords as the methodology says, like the DM slides.
- Methodology slide: removed a non-existent "İlk Cevap Veren" entry, added "Sabah Kuşu", DM "Sohbet Ritmi" is monthly (not weekly), and the footnote names the selected period. In the PDF all entries now fit on the page (the scroll box cut it to 6).
- Words are lowercased the Turkish way: caps words with "İ" ("NEREDESİN") were split into fragments; words with â/î/û stay whole.
- Mentions of names starting or ending with Turkish letters ("Çağla", "Ömür") were never counted.
- Multi-line messages kept only their first line; the rest is now part of the message. A line containing " - " or ": " is no longer misread as a new message.
- iOS encryption notice on the first line is no longer counted as a message from a member named after the group; in DMs it no longer removes the contact.
- Arabic/CJK messages no longer count as caps lock; contacts named "constructor" or words like "toString" no longer break the analysis; names containing "$" show without a stray backslash and can be renamed.
- Slides with no possible winner (e.g. nobody wrote in caps) show "Yok" instead of the alphabetically first person.
- "Sabah İlk Cevap Veren" subtitle wrongly said the winner answers their own good morning; response times under a minute show "< 1 dk" instead of "0 dk".
- Weekly chart labels were a day early for users west of UTC.
- **Mobile**: compact two-row deck controls, big dates/hours shrink instead of being clipped, one-column methodology, no iOS zoom when editing names, scrollable slides on landscape phones, no sticky hover colors after a tap, PDF export from a phone keeps the desktop slide layout.
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
- External links in the footer open with `rel="noopener noreferrer"`.
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
