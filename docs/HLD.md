# High-Level Design (HLD)

## 1. Introduction

The **VITTI Engine** is a high-performance content orchestration platform designed for Vitti Capital. It automates the extraction, curation, and generation of premium LinkedIn content using a sophisticated hybrid AI pipeline.

## 2. Core Architecture

The system follows a **Decoupled Hybrid Architecture**, separating deep research from creative drafting to ensure maximal content quality and data grounding.

### System Components:

1. **The Researcher (Perplexity AI - sonar-pro)**
   - **Data Extraction**: Performs live internet searches for Australian financial news and tech trends.
   - **Grounding Layer**: Extracts raw facts, percentages, and named entities to form the foundation of every post.
   - **Quality Filtering**: Integrated prompts ensure only structured, verifiable data is passed forward.

2. **The Creative Director (GROQ AI - Llama-3.3-70b)**
   - **Drafting Layer**: Transforms raw research into high-engagement, human-centric LinkedIn posts.
   - **Persona Enforcement**: Implements the Vitti Capital CEO persona (Shubham Goyal), ensuring a professional, institutional tone.
   - **Structured Ideas**: Generates multi-layered content ideas consisting of a hook, context, and strategic angle.

3. **The Orchestration Layer (GitHub Actions)**
   - **Daily Execution**: A scheduled cron job (@ 9:00 AM UTC) triggers the full content generation cycle.
   - **State Management**: Automatically commits log files and updates the `used_bookmarks.txt` registry to prevent duplicate content.

4. **The UI Dashboard (Next.js)**
   - **Data Visualization**: Renders structured JSON logs into a premium, animated glassmorphism dashboard.
   - **One-Click Publishing**: Direct-to-LinkedIn sharing via a custom Unicode polyfill to bypass URI truncation bugs.
   - **Remote Triggering**: Manual `workflow_dispatch` capability via the GitHub API.

## 3. Data Flow Execution Diagram

```text
[User] -> Opens Dashboard -> Dashboard reads `/logs/**/*.json` -> User views Posts.

[User/Cron] -> Trigger Execution
   |
   +-> [GitHub Actions Workflow]
         |
         +-> [Researcher: Perplexity] -> Hunts for News / Bookmarks
         |     |
         |     +-> [Quality Gate] -> Rejects vague/data-less items
         |
         +-> [Creative Director: Groq] -> Drafts Posts & Structured Ideas
         |
         +-> [Sync Layer]
               |
               +-> Google Docs (Prepends readable text)
               +-> JSON Logs (Saves structured data for Dashboard)
               +-> GIT Push (Saves Logs & Cache to Repo)
```

## 4. Logical Components

- **CEO Pipeline**: Focuses on institutional financial news and market stabilisations.
- **Raindrop Hybrid Pipeline**: Merges personal bookmarks with trending business news fallback.
- **Idea Engine**: Generates strategic content hooks backed by real-world context and specific "angles".
