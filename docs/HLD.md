# High-Level Design (HLD)

## 1. Introduction

The **VITTI Engine** is a high-performance idea generation platform designed for Vitti Capital. It automates the extraction, curation, and generation of a daily pack of finance ideas grounded in multiple sources.

## 2. Core Architecture

The system follows a **multi-source grounding architecture**, combining personal bookmarks with trending finance news before generating a connected idea series.

### System Components:

1. **Sources (Raindrop + Trending News RSS)**
   - **Bookmarks**: Pulls unused Raindrop bookmarks as personal context.
   - **Trending News**: Pulls current finance/business headlines via RSS queries (Australia + global).
   - **Source Mixing Goal**: Ensures we do not rely on a single source type.

2. **Generator (Claude Opus 4.6)**
   - **Single-pass generation**: One LLM call consumes combined sources.
   - **Connected Series Output**: Produces exactly 5 ideas/day where each idea builds on the previous.
   - **Finance-first content**: Each idea includes a 1-pager or multi-pager content plan (actual markdown pages).

3. **The Orchestration Layer (GitHub Actions)**
   - **Daily Execution**: A scheduled cron job (@ 9:00 AM UTC) triggers the full content generation cycle.
   - **State Management**: Automatically commits log files and updates the `used_bookmarks.txt` registry to prevent duplicate content.

4. **The UI Dashboard (Next.js)**
   - **Data Visualization**: Renders structured JSON logs into a premium, animated glassmorphism dashboard.
   - **Remote Triggering**: Manual `workflow_dispatch` capability via the GitHub API.

## 3. Data Flow Execution Diagram

```text
[User] -> Opens Dashboard -> Dashboard reads `/logs/**/*.json` -> User views Ideas.

[User/Cron] -> Trigger Execution
   |
   +-> [GitHub Actions Workflow]
         |
         +-> [Sources] -> Fetch Raindrop Bookmarks + Trending News (RSS)
         |
         +-> [Claude Opus 4.6] -> Generates 5 connected finance ideas + pager content
         |
         +-> [Sync Layer]
               |
               +-> Google Docs (Ideas only)
               +-> JSON Logs (Ideas only)
               +-> GIT Push (Saves logs & used_bookmarks.txt)
```

## 4. Logical Components

- **Daily Ideas Pack**: A single pipeline that always mixes sources (bookmarks + trending news).
- **Connected-Series Idea Engine**: Produces 5 ideas/day that are related and build on each other.
- **Pager Content Builder**: Each idea includes 1-pager or multi-pager markdown content.
