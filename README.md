# VITTI Engine: Hybrid AI Content Pipeline

An elite, high-performance idea generation engine for **Vitti Capital**. This system automates the transformation of Raindrop.io bookmarks and trending finance news into a daily pack of connected, data-backed content ideas.

Powered by **Claude** and managed via a premium **Next.js Glassmorphism Dashboard**.

---

## Key Features

### Data-Backed Quality Gates
Unlike generic AI engines, VITTI enforces strict **Quality Gates**. 
- **Entity Verification**: News items are discarded unless they contain specific numbers (%, $) or named entities/tickers.
- **Bracket-Depth Extraction**: Robust JSON parsing that intelligently skips AI citation markers (e.g., `[1]`) to ensure valid data.
- **Persona Enforcement**: Hard constraints prevent "AI-speak". Rejects vague or short outputs entirely.

### Hybrid AI Architecture
- **Sources (Bookmarks + Trending News)**: Pulls curated Raindrop bookmarks and trending finance/business news (via RSS).
- **Claude (Anthropic)**: Generates a daily pack of connected ideas (and 1-pager/multi-pager content) grounded in the combined sources.

### Premium Dashboard
- **Glassmorphism Design**: A stunning Zinc/Violet interface with the *Outfit* font, radial gradients, and micro-animations.
- **Structured Rendering**: Custom cards for **Ideas** (hook, context, angle, and source badges).
- **Remote Orchestration**: Trigger GitHub Action workflows directly from the web interface.

---

## Technical Stack

- **Backend**: Python 3.11+, Anthropic (Claude) API, Google Docs API.
- **Frontend**: Next.js 14, TailwindCSS (for foundational layout), Vanilla CSS (for premium effects), Framer Motion.
- **Infrastructure**: GitHub Actions (Daily Cron @ 9:00 AM UTC).

---

## Secrets & Setup

### GitHub Repository Secrets
To run the cloud engine, you **must** configure these Secrets:
- `ANTHROPIC_API_KEY`: For Claude generation.
- `ANTHROPIC_MODEL` (optional): Model name override (defaults in code).
- `RAINDROP_TOKEN`: For pulling curated bookmarks.
- `GOOGLE_CREDENTIALS`: Raw JSON string of your Google Service Account.
- `IDEAS_DOC_ID`: Target Google Doc ID for ideas (only doc written).

### Local Development (Dashboard)
1. Navigate to the `/web` directory.
2. `npm install`
3. Create `.env.local`:
   ```env
   GITHUB_PAT=your_github_token
   GITHUB_REPO=username/repo
   ```
4. `npm run dev`

---

## Architecture
- **[High-Level Design (HLD)](docs/HLD.md)** - System flow and infra.
- **[Low-Level Design (LLD)](docs/LLD.md)** - Code logic and quality gates.

---
*Developed with 💙 by [Tushar Bhardwaj](https://minianonlink.vercel.app/tusharbhardwaj)*