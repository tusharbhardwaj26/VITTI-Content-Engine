# Low-Level Design (LLD)

## 1. Python Generation Modules

### `generate_raindrop_posts.py` (Daily Ideas Pack Generator)
- **`fetch_raindrop_bookmarks()`**: Pulls unused Raindrop bookmarks and tracks consumption via `web/used_bookmarks.txt`.
- **`fetch_trending_finance_news()`**: Pulls trending finance/business headlines via RSS queries (Australia + global) to avoid relying on a single source.
- **`generate_daily_connected_ideas(sources, ideas_per_day=5)`**: Single Claude call that consumes combined sources and returns exactly 5 connected ideas (a themed series). Each idea includes 1-pager or multi-pager markdown content.
- **`parse_and_filter_ideas(ideas_list)`**: Validates the structured idea objects. Ensures every idea contains a `title`, `context`, and `angle`. Rejects any idea containing generic phrases like "In today's fast-paced world".
- **`format_ideas_for_doc(ideas)`**: Converts the structured JSON idea objects into human-readable plain text for Google Docs, using custom separators and formatted sections.
- **`save_to_logs(data, subfolder)`**: Implements a safe `_load_log_file` helper which prevents runtime crashes if a log file is empty or corrupted during a GitHub Actions race condition.

## 2. Next.js Dashboard & UX Logic

### `src/app/page.js` (Premium UI Engine)
- **Ideas-only Dashboard**: The UI renders only the Ideas feed and exposes a single pipeline trigger.
- **`Skeleton Screens`**: Uses CSS animations to provide a premium loading experience while the dashboard fetches the latest logs from the daily artifacts.

### `src/app/api/cache/route.js`
- **Smart Directory Resolution**: Automatically detects if the API is running in a local dev environment or a production CI environment to resolve the relative path to the `/logs` root.
- **Safe JSON Parsing**: Implements a try-catch wrapper around `JSON.parse` that gracefully returns `null` for empty files, preventing the entire dashboard from breaking if a daily generation fails.

## 3. Data Schema Definitions

### Content Idea Object
```json
{
  "series_title": "Shared theme for the 5 ideas",
  "series_thesis": "1-2 sentences",
  "title": "The Hook",
  "context": "The underlying data/market fact",
  "angle": "The unique strategic take",
  "connections": { "builds_on": "How this connects to the previous idea" },
  "grounding": { "sources_used": [{ "source_type": "raindrop|news", "title": "...", "url": "..." }] },
  "source_type": "hybrid",
  "region": "Australia | Global | Mixed",
  "content": {
    "format": "1-pager|multi-pager",
    "pages": [{ "page_title": "Page title", "markdown": "..." }]
  }
}
```
