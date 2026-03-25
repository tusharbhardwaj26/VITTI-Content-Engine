# Low-Level Design (LLD)

## 1. Python Generation Modules

### `generate_ceo_posts.py` (CEO Post Generator)
- **`is_news_item_strong(item)`:** Implements the core quality gate. Uses regex to scan for high-density digits (`%`, `$`) and specific named entities or ASX tickers. Discards generic "filler" news.
- **`extract_first_json_array(text)`:** A sophisticated bracket-depth walker. It specifically looks for the first balanced `[...]` structure starting with `[{`, which allows it to intelligently bypass and ignore LLM citation markers (e.g., `[1]`, `[2]`) that frequently break standard regex parsers.
- **`generate_ceo_linkedin_post(item)`**: Hard persona integration. Uses Groq's high-speed inference to draft posts that adhere to strict length (150-250 words) and "no corporate buzzword" constraints.

### `generate_raindrop_posts.py` (Raindrop Ideas Generator)
- **`parse_and_filter_ideas(ideas_list)`**: Validates the structured idea objects. Ensures every idea contains a `title`, `context`, and `angle`. Rejects any idea containing generic phrases like "In today's fast-paced world".
- **`format_ideas_for_doc(ideas)`**: Converts the structured JSON idea objects into human-readable plain text for Google Docs, using custom separators and formatted sections.
- **`save_to_logs(data, subfolder)`**: Implements a safe `_load_log_file` helper which prevents runtime crashes if a log file is empty or corrupted during a GitHub Actions race condition.

## 2. Next.js Dashboard & UX Logic

### `src/app/page.js` (Premium UI Engine)
- **`LinkedInIcon`**: A custom, official SVG implementation of the LinkedIn logo to replace the generic Lucide icon.
- **`Unicode Polyfill`**: A critical sharing fix. Appends a Zero-Width Space (`\u200B`) and replaces `?`, `&`, and `#` with their visually identical Fullwidth Unicode counterparts (`\uFF1F`, `\uFF06`, `\uFF03`). This bypasses the browser's native URL truncation and LinkedIn's internal router bug, ensuring 3000+ character posts can be shared with one click.
- **`Skeleton Screens`**: Uses CSS animations to provide a premium loading experience while the dashboard fetches the latest logs from the daily artifacts.

### `src/app/api/cache/route.js`
- **Smart Directory Resolution**: Automatically detects if the API is running in a local dev environment or a production CI environment to resolve the relative path to the `/logs` root.
- **Safe JSON Parsing**: Implements a try-catch wrapper around `JSON.parse` that gracefully returns `null` for empty files, preventing the entire dashboard from breaking if a daily generation fails.

## 3. Data Schema Definitions

### Content Idea Object
```json
{
  "title": "The Hook",
  "context": "The underlying data/market fact",
  "angle": "The unique strategic take",
  "source_type": "raindrop | news",
  "region": "Australia | Global"
}
```

### CEO Post Object
```json
{
  "topic": "The ASX/Financial Headline",
  "post": "The drafted 200-word LinkedIn post"
}
```
