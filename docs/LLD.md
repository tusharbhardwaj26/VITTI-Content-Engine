# Low-Level Design (LLD)

## 1. Entry point: `generate_raindrop_posts.py`

### Environment

| Variable | Purpose |
|----------|---------|
| `RAINDROP_TOKEN` | Bearer token for Raindrop API |
| `ANTHROPIC_API_KEY` or `CLAUDE_API_KEY` | Claude API |
| `ANTHROPIC_MODEL` | Optional model id (code has a default) |
| `IDEAS_DOC_ID` | Target Google Doc |
| `GOOGLE_CREDENTIALS_JSON` | Path to service account JSON file |
| `DISABLE_GOOGLE_DOC` | If truthy, skip Doc API writes |
| `FALLBACK_ON_LLM_FAILURE` | Debug-only; not used for production log writes |

`load_dotenv()` loads a root `.env` when present.

### Core functions

| Function | Behavior |
|----------|----------|
| `fetch_raindrop_bookmarks()` | GET raindrops; skip IDs in `web/used_bookmarks.txt`; split pinned vs not; return up to five (pinned first). |
| `fetch_trending_finance_news()` / `fetch_trending_tech_news()` | Google News RSS–style URLs; dedupe by title; respect recency window. |
| `attach_cross_verification(anchors, external_items, per_anchor)` | Score overlap; attach up to `per_anchor` URLs; fill from pool if weak overlap. |
| `pick_diverse_web_anchors(finance, tech, count)` | Alternate pools + dedupe keys for web-only mode. |
| `dedupe_source_list(items)` | Dedupe by URL or title before sending giant payloads. |
| `fetch_url_snippet(url)` | Optional HTML snippet for empty Raindrop excerpts (best-effort). |
| `generate_daily_connected_ideas(sources, ideas_per_day, source_mode)` | Builds `compact_sources` (includes `cross_verify`); prompts Claude; returns raw text. |
| `_normalize_idea_fields(idea)` | Merges `linkedin_playbook` into `context`/`angle`/`title` when needed; fixes occasional key typos. |
| `parse_and_filter_ideas(raw)` | JSON extract via `extract_first_json_array`; generic-phrase filter; requires title, context, angle after normalization. |
| `format_ideas_for_doc(ideas)` | Plain text for Google Doc: playbook fields, sources, draft excerpt. |
| `save_to_logs(ideas)` | Append to `web/logs/{date}.json`. |
| `append_to_google_doc(...)` | Prepend to Doc; respects size trim helpers; skips if disabled or missing creds. |

### Main control flow (simplified)

1. Load bookmarks; enrich with optional snippet.
2. Load finance + tech RSS; fail if empty.
3. If bookmarks: `source_mode = raindrop_plus_web`; attach cross-verify from RSS; `used_ids` = bookmark ids.
4. Else: `source_mode = web_only`; `pick_diverse_web_anchors`; attach cross-verify from rest pool; `used_ids` = [].
5. Call Claude; optional debug fallback (does not commit logs in success path).
6. Parse; require **exactly five** ideas (unless fallback debug path).
7. Write Doc + log + `mark_bookmark_used` only on success.

### JSON extraction

`extract_first_json_array` walks bracket depth to find first `[{...}]` or a single object, stripping ``` fences—reduces breakage from stray `[1]` citations.

---

## 2. Next.js application (`web/`)

### `src/app/api/cache/route.js`

- Resolves `logs` dir: `process.cwd()/logs` or `process.cwd()/web/logs`.
- **Available dates:** scan **root** `*.json` (not `ideas/` subfolder).
- **Load:** `ideas` = last element of parsed array in `YYYY-MM-DD.json`.
- Response: `{ ideas, availableDates, selectedDate }`.

### `src/app/api/trigger/route.js`

- POST: GitHub `workflow_dispatch` on `generate.yml` using `GITHUB_PAT` + `GITHUB_REPO`.

### `src/app/page.js`

- Fetches `/api/cache`; renders **Ideas only**.
- **IdeaCard:** series strip; badges; LinkedIn playbook (hook, why, unique take, CTA, poll list); **lightbulb** toggles popover for `why_this_works`; **Headline** when draft exists; **Context/angle** hidden when draft exists to reduce duplication.
- **Copy:** copies concatenated pager markdown (“Copy draft”) or fallback to title/context/angle.
- Single-page pager auto-opens once via `useEffect` + `pagerInitialized`.

### `src/app/globals.css`

- Design tokens, glass cards, pager accordion styles.

---

## 3. Data schema (idea object)

Minimal shape stored in logs (exact fields may vary slightly by model):

```json
{
  "series_title": "string",
  "series_thesis": "string",
  "title": "string",
  "context": "string",
  "angle": "string",
  "connections": { "builds_on": "string" },
  "linkedin_playbook": {
    "format_name": "string",
    "opening_hook": "string",
    "why_section": "string",
    "unique_take": "string",
    "call_to_action": "string",
    "why_this_works": "string",
    "poll_options": ["optional"]
  },
  "grounding": {
    "sources_used": [
      { "source_type": "raindrop|news|tech|web", "title": "string", "url": "string" }
    ]
  },
  "region": "Australia|Global|Mixed",
  "source_type": "hybrid",
  "content": {
    "format": "1-pager|multi-pager",
    "pages": [
      { "page_title": "string", "markdown": "string" }
    ]
  }
}
```

---

## 4. Files & paths

| Path | Role |
|------|------|
| `generate_raindrop_posts.py` | Daily generator |
| `web/logs/YYYY-MM-DD.json` | Dashboard input |
| `web/used_bookmarks.txt` | Raindrop IDs consumed |
| `.github/workflows/generate.yml` | CI schedule + run |
| `requirements.txt` | Python deps (e.g. `anthropic`, Google clients, `requests`) |

---

## 5. Failure behavior

- **Claude errors / overload:** retries with backoff; if still no valid five ideas, process exits **without** writing logs or consuming bookmarks.
- **Empty RSS:** hard exit (cannot cross-verify).
- **Malformed log file:** `_load_log_file` returns `[]` and starts fresh on write.
