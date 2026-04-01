# Vitti Ideas Engine

**A daily assistant that turns saved articles and live market news into five ready-to-use LinkedIn-style content ideas**—with sources checked against each other so ideas are not built from a single headline.

Built for **Vitti Capital**. The system runs on a schedule (or on demand), saves results where your team can read them, and optionally syncs one Google Doc.

---

## What this does (simple)

1. **Collects inputs**
   - **First:** up to five unused items from **Raindrop** (pinned items are preferred). Items you have already used are skipped so you do not repeat the same idea.
   - **Always:** recent **finance** and **tech** headlines from the web (via news feeds). This is used to **cross-check** Raindrop stories—or, if Raindrop has nothing new, to drive the whole run from the web with mixed sources.

2. **Creates five linked ideas for the day**
   - A smart model (**Claude**, from Anthropic) reads everything together and writes **five ideas** that share one **theme** for the day. Each idea includes structure for LinkedIn (hook, why it matters, angle, call to action) and a **draft** you can copy.

3. **Saves outputs**
   - **Log file:** one file per day, e.g. `web/logs/2026-04-01.json`, for your **dashboard** website.
   - **Google Doc (optional):** the same ideas can be **prepended** into one Ideas document for archiving or editing.

**You do not need to be technical** to understand the flow: save articles in Raindrop (or rely on web news), let the job run, then open the dashboard or the Doc and use the drafts.

---

## What you get each day

| Output | What it is |
|--------|------------|
| **Five ideas** | One connected “series” so the day feels cohesive, not random. |
| **Cross-checking** | Ideas tie **multiple sources** together (e.g. two news angles on the same theme). |
| **LinkedIn-minded structure** | Each idea can include playbook fields (hook, why it matters, unique take, CTA) plus a **markdown draft** for posting. |
| **No duplicate Raindrop use** | Used bookmark IDs are stored so the same pinned item is not reused automatically. |

---

## How it runs

```text
Scheduled time (or manual “Run”) 
    → Fetch Raindrop (if any) + web feeds 
    → Cross-verify and bundle sources 
    → Claude writes 5 ideas 
    → Save JSON log + update Google Doc (if configured) 
    → Dashboard reads the latest log
```

For a **technical diagram** and terms, see [docs/HLD.md](docs/HLD.md). For **functions, files, and data shape**, see [docs/LLD.md](docs/LLD.md).

---

## Who does what

| Piece | Role |
|-------|------|
| **Raindrop** | Your library of articles; pinned items are preferred when picking up to five unused items. |
| **Web feeds** | Live finance and tech headlines so ideas are not based on one story alone. |
| **Claude** | Writes the five connected ideas and drafts from the combined material. |
| **GitHub Actions** | Runs the generator on a **daily schedule** and can be **triggered manually** from the dashboard (if you configure GitHub). |
| **Next.js dashboard** | Shows the latest ideas from the log files; **Copy draft** copies the post text; a **lightbulb** explains why a given LinkedIn format fits (when present). |
| **Google Doc** | Optional archive of the same ideas in one document. |

---

## For technical readers

### Stack

- **Generator:** Python 3 (`generate_raindrop_posts.py`) — Raindrop API, RSS, Anthropic API, optional Google Docs API.
- **Dashboard:** Next.js app under `web/` — reads `web/logs/*.json` via `/api/cache`.
- **Automation:** `.github/workflows/generate.yml` — install deps, run generator, commit logs when configured.

### Repository secrets (GitHub Actions)

Configure in your repo **Settings → Secrets and variables → Actions**:

- `ANTHROPIC_API_KEY` — Claude API key (or align with your env; locally `CLAUDE_API_KEY` is also supported by the script).
- `ANTHROPIC_MODEL` — optional; defaults to Opus-class model in code.
- `RAINDROP_TOKEN` — Raindrop.io API token.
- `GOOGLE_CREDENTIALS` — service account JSON (single string secret) used to create the credentials file in CI.
- `IDEAS_DOC_ID` — Google Doc ID for ideas (**only** Doc written by this pipeline).

### Local quick test

From the repository root:

```bash
pip install -r requirements.txt
python generate_raindrop_posts.py
```

Use a `.env` file for keys if you prefer (see LLD). To skip Google Doc locally, you can set `DISABLE_GOOGLE_DOC=1`.

### Local dashboard

```bash
cd web
npm install
npm run dev
```

Add `web/.env.local` with `GITHUB_PAT` and `GITHUB_REPO` if you want the “run pipeline” button to dispatch GitHub Actions.

---

## License / credits

Developed with care by [Tushar Bhardwaj](https://minianonlink.vercel.app/tusharbhardwaj).
