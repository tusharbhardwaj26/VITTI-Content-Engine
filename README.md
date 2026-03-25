# VITTI Engine: Hybrid AI Content Pipeline

An elite, high-performance content generation engine for **Vitti Capital**. This system automates the transformation of Australian financial news and Raindrop.io bookmarks into premium, data-backed LinkedIn content.

Powered by a **Hybrid AI Architecture** (Perplexity for deep research + GROQ Llama-3.3-70b for creative drafting) and managed via a premium **Next.js Glassmorphism Dashboard**.

---

## Key Features

### Data-Backed Quality Gates
Unlike generic AI engines, VITTI enforces strict **Quality Gates**. 
- **Entity Verification**: News items are discarded unless they contain specific numbers (%, $) or named entities/tickers.
- **Bracket-Depth Extraction**: Robust JSON parsing that intelligently skips AI citation markers (e.g., `[1]`) to ensure valid data.
- **Persona Enforcement**: Hard constraints prevent "AI-speak". Rejects vague or short outputs entirely.

### Hybrid AI Architecture
- **Perplexity (sonar-pro)**: Acts as the "Researcher", hunting through real-time Australian financial news and web data.
- **GROQ (llama-3.3-70b-versatile)**: Acts as the "Creative Director", taking raw facts and drafting high-engagement, human-centric posts at lightning speed.

### Premium Dashboard
- **Glassmorphism Design**: A stunning Zinc/Violet interface with the *Outfit* font, radial gradients, and micro-animations.
- **Structured Rendering**: Custom cards for **CEO Posts**, **LinkedIn Drafts**, and **Content Ideas** (including hook, context, and angle analysis).
- **One-Click Publishing**: Direct-to-LinkedIn sharing with a **Unicode Polyfill** that bypasses browser-native truncation bugs for long posts.
- **Remote Orchestration**: Trigger GitHub Action workflows directly from the web interface.

---

## Technical Stack

- **Backend**: Python 3.11+, Perplexity API, Groq API, Google Docs API.
- **Frontend**: Next.js 14, TailwindCSS (for foundational layout), Vanilla CSS (for premium effects), Framer Motion.
- **Infrastructure**: GitHub Actions (Daily Cron @ 9:00 AM UTC).

---

## Secrets & Setup

### GitHub Repository Secrets
To run the cloud engine, you **must** configure these Secrets:
- `PERPLEXITY_API_KEY`: For real-time web research.
- `GROQ_API_KEY`: For high-speed creative drafting.
- `RAINDROP_TOKEN`: For pulling curated bookmarks.
- `GOOGLE_CREDENTIALS`: Raw JSON string of your Google Service Account.
- `CEO_LINKEDIN_DOC_ID` / `IDEAS_DOC_ID` / `LINKEDIN_POSTS_DOC_ID`: Target Google Doc IDs.

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