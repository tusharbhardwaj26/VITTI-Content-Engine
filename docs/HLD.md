# High-Level Design (HLD)

## 1. Purpose

The **Vitti Ideas Engine** produces **five connected content ideas per day** for professional LinkedIn-style publishing. Ideas are grounded in **multiple sources**: Raindrop bookmarks (pinned first) and live **finance + tech** headlines from RSS. A single language-model pass turns that bundle into structured output (playbook + draft text), then persists it to **JSON logs** and optionally **one Google Doc**.

## 2. Design principles

| Principle | Meaning |
|-----------|---------|
| **Multi-source** | No idea is meant to rest on one URL; Raindrop items get `cross_verify` rows from web items; web-only runs use mixed anchors. |
| **Pinned preference** | Unused Raindrop items are ordered with **important/pinned** first, then others, capped at five per run. |
| **No reuse spam** | Consumed Raindrop IDs are appended to `web/used_bookmarks.txt`. |
| **Deterministic outputs** | Exactly **five** valid ideas required for a successful run; otherwise no log write and no bookmark consumption (avoids bad or partial days). |
| **Single archive doc** | Only the **Ideas** Google Doc is written by this pipeline. |

## 3. Major components

1. **Source layer**
   - **Raindrop REST API:** raindrops collection, filter by “not in used list”, prefer `important`.
   - **RSS aggregation:** separate finance and tech query feeds (Australia + global mix).
   - **Cross-verification:** each anchor row gets related rows from another pool (token overlap + fallback diversity).

2. **Generation layer**
   - **Anthropic Claude:** one request per day with full `SOURCE JSON` (including `cross_verify`).
   - **Modes:** `raindrop_plus_web` when bookmarks exist; `web_only` when none (diverse web anchors + cross-verify).

3. **Persistence layer**
   - **Logs:** `web/logs/YYYY-MM-DD.json` — append-only array of daily `{ timestamp, ideas }` entries.
   - **Google Docs:** prepend human-readable block (playbook + sources + draft snippet) to `IDEAS_DOC_ID` when credentials exist and writes are enabled.

4. **Presentation layer (Next.js)**
   - **GET `/api/cache`:** discovers dates from `web/logs/*.json`, returns latest run’s `ideas` for selected date.
   - **Dashboard:** renders idea cards: series, badges, LinkedIn playbook sections, pager draft, **lightbulb** popover for “why this format works”, **Copy draft** for markdown.

5. **Orchestration (GitHub Actions)**
   - Cron + `workflow_dispatch`; runs Python, writes artifacts, may commit `web/logs` and `used_bookmarks.txt`.

## 4. End-to-end flow

```text
[Cron or “Run workflow”]
        │
        ▼
┌───────────────────┐
│ Fetch Raindrop    │── unused IDs, pinned first (max 5)
│ + Finance RSS     │
│ + Tech RSS        │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Attach cross-     │── per-anchor related items (non–single-source)
│ verification      │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Claude            │── 5 ideas, series + linkedin_playbook + drafts
│ (single call)     │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐     ┌────────────────────┐
│ Validate / parse  │────►│ Exit without write │
│ (exactly 5 ideas)│     │ if incomplete      │
└─────────┬─────────┘     └────────────────────┘
          │ success
          ▼
┌───────────────────┐     ┌───────────────────┐
│ web/logs/DATE.json│     │ Google Doc (opt.) │
│ + used_bookmarks  │     │ IDEAS_DOC_ID      │
└───────────────────┘     └───────────────────┘
          │
          ▼
   [Dashboard reads latest log]
```

## 5. Logical building blocks

- **Daily Ideas Pack:** one themed set of five ideas.
- **Cross-verify bundle:** structured JSON passed to Claude so every anchor has peer stories.
- **LinkedIn playbook:** optional structured fields (format name, hook, sections, CTA, why format works) plus `content.pages[].markdown` as the post draft.
- **Web-only path:** activates when Raindrop returns zero usable items; uses `pick_diverse_web_anchors` + same cross-verify discipline.

## 6. Out of scope (current)

- CEO / separate LinkedIn pipeline, multiple Google Docs, or Perplexity/Groq in this repo path.
- Full browser rendering or paywalled article extraction (RSS + light optional URL fetch only).
