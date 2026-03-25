import os
import requests
import json
import re
from datetime import datetime, timezone, timedelta
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import pytz
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

RAINDROP_TOKEN = os.getenv("RAINDROP_TOKEN")
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON", "vitti-ideas-e5256b131985.json")
GOOGLE_DOC_ID = os.getenv("IDEAS_DOC_ID")
NEW_GOOGLE_DOC_ID = os.getenv("LINKEDIN_POSTS_DOC_ID")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_MODEL = "sonar-pro"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

DOC_SIZE_LIMIT = 800_000
TRIM_TARGET = 500_000

def utf16_len(text):
    return len(text.encode("utf-16-le")) // 2

def get_used_bookmarks():
    if os.path.exists('web/used_bookmarks.txt'):
        with open('web/used_bookmarks.txt', 'r', encoding='utf-8') as f:
            return set(f.read().splitlines())
    return set()

def mark_bookmark_used(bm_id):
    if not bm_id: return
    with open('web/used_bookmarks.txt', 'a', encoding='utf-8') as f:
        f.write(f"{bm_id}\n")

def fetch_raindrop_bookmarks():
    used_bms = get_used_bookmarks()
    headers = {"Authorization": f"Bearer {RAINDROP_TOKEN}"}
    response = requests.get(
        f"https://api.raindrop.io/rest/v1/raindrops/0?perpage=50",
        headers=headers
    )
    if response.status_code != 200:
        print(f"Raindrop Error: {response.text}")
        return []
        
    items = response.json().get("items", [])
    recent_bookmarks = []
    
    for item in items:
        bm_id = str(item.get("_id", ""))
        if bm_id in used_bms:
            continue
        recent_bookmarks.append({
            "id": bm_id,
            "title": item.get("title", ""),
            "excerpt": item.get("excerpt", "")
        })
        if len(recent_bookmarks) >= 5:
            break
            
    return recent_bookmarks

def _call_groq(prompt, temperature=0.7):
    if not groq_client:
        print("❌ GROQ_API_KEY is missing!")
        return ""
    try:
        completion = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=4000
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Groq Error: {e}")
        return ""

def _call_perplexity(prompt, temperature=0.7):
    if not PERPLEXITY_API_KEY:
        print("❌ PERPLEXITY_API_KEY is missing!")
        return ""
        
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": PERPLEXITY_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": 4000
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code == 200:
            return response.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        else:
            print(f"❌ Perplexity Error {response.status_code}: {response.text}")
            return ""
    except Exception as e:
        print(f"❌ Perplexity Exception: {e}")
        return ""

def generate_ideas(content_item):
    text = f"Title: {content_item.get('title', '')}\nExcerpt: {content_item.get('excerpt', '')}"
    source_type = content_item.get('source_type', 'raindrop')

    prompt = f"""You are a content strategist. Based on the real-world source below, generate 2-3 LinkedIn post ideas.

SOURCE ({source_type.upper()}):
{text}

STRICT RULES:
- Each idea MUST be grounded in the source above — do NOT invent new topics.
- Each idea MUST reference a real event, trend, data point, or observation from the source.
- REJECT ideas that are motivational, generic, or have no real-world anchor.
- If the source is too vague to produce real ideas, output an empty JSON array [].

OUTPUT FORMAT: strict JSON array ONLY, no markdown, no preamble.
[
  {{
    "title": "Punchy, specific hook that could stop a scroll",
    "context": "The real-world event, data, or observation this is based on (1-2 sentences)",
    "angle": "Why this is interesting or non-obvious for a professional audience (1 sentence)",
    "source_type": "{source_type}",
    "region": "Australia or Global"
  }}
]

Generate now:"""

    raw = _call_groq(prompt, 0.5)
    return raw

def parse_and_filter_ideas(raw_ideas_str):
    """Parse GROQ JSON output and reject generic/ungrounded ideas."""
    if not raw_ideas_str:
        return []
    try:
        raw_ideas_str = raw_ideas_str.replace("```json", "").replace("```", "").strip()
        match = re.search(r'\[.*\]', raw_ideas_str, re.DOTALL)
        ideas = json.loads(match.group()) if match else json.loads(raw_ideas_str)
    except Exception as e:
        print(f"  ⚠️ Could not parse ideas JSON: {e}")
        return []

    GENERIC_PHRASES = [
        "consistency is key", "hard work pays off", "believe in yourself",
        "embrace the journey", "think outside the box", "leverage", "synergy",
        "in today's world", "fast-paced", "game changer", "disrupt"
    ]

    filtered = []
    for idea in ideas:
        if not isinstance(idea, dict):
            continue
        title = idea.get('title', '').lower()
        context = idea.get('context', '').lower()
        angle = idea.get('angle', '')
        # Reject if missing required fields
        if not title or not context or not angle:
            print(f"  ⚠️ REJECTED (missing fields): {idea.get('title', '')[:60]}")
            continue
        # Reject generic phrases
        if any(phrase in title or phrase in context for phrase in GENERIC_PHRASES):
            print(f"  ⚠️ REJECTED (generic): {idea.get('title', '')[:60]}")
            continue
        filtered.append(idea)
    return filtered

def generate_linkedin_post(idea):
    """Generate one LinkedIn post from a structured idea object."""
    if isinstance(idea, dict):
        idea_text = (
            f"Title/Hook: {idea.get('title', '')}\n"
            f"Context: {idea.get('context', '')}\n"
            f"Angle: {idea.get('angle', '')}\n"
            f"Region: {idea.get('region', 'Australia')}"
        )
    else:
        idea_text = str(idea)

    prompt = f"""Write a LinkedIn post based STRICTLY on the idea below. Do not invent new topics.

IDEA:
{idea_text}

STRICT RULES:
✅ Open with a single punchy, scroll-stopping headline (1 line).
✅ Expand with real context from the idea — reference the data, event, or observation mentioned.
✅ Give a clear, practical insight for a professional audience.
✅ End with ONE sharp question that forces a thoughtful comment.
✅ 150–250 words. Conversational but professional. No fluff, no AI jargon.
✅ No emojis excessively. No ** bolding. No [1] citations.

If the idea has no real context to expand on, respond ONLY with: SKIP

Write the post now:"""

    post = _call_groq(prompt, 0.65)
    post = post.replace("**", "")
    post = re.sub(r'\[\d+\]', '', post)
    if post.strip().upper() == "SKIP" or len(post.strip()) < 80:
        print(f"  ⚠️ GROQ returned SKIP or empty for idea: {idea.get('title', '') if isinstance(idea, dict) else str(idea)[:60]}")
        return ""
    return post

def fetch_web_ideas(needed_count):
    if needed_count <= 0: return []
    prompt = f"""Search the web RIGHT NOW for {needed_count} significant Australian financial or business news stories published in the last 24-48 hours.

    STRICT REQUIREMENTS for each story:
    - Must be real, verifiable, and recent (last 48 hours)
    - Must include specific numbers: %, $, growth rate, volume, index points, etc.
    - Must be in one of these areas ONLY: ASX, Australian real estate, M&A/PE/VC in Australia, RBA/macro economy, commodities
    - Reject vague articles, opinion pieces without data, or lifestyle/motivational content

    Output as strict JSON array ONLY, no markdown:
    [{{"title": "specific headline with numbers", "excerpt": "key facts with data points", "source_type": "news", "region": "Australia"}}]"""
    content = _call_perplexity(prompt, 0.2)
    try:
        match = re.search(r'\[.*\]', content, re.DOTALL)
        if match:
            return json.loads(match.group())
        return json.loads(content)
    except:
        print("  ⚠️ Could not parse web ideas JSON. Returning empty.")
        return []

def format_ideas_for_doc(ideas_structured):
    """Convert structured idea dicts into clean human-readable text for Google Docs."""
    lines = []
    for idx, idea in enumerate(ideas_structured, 1):
        lines.append(f"IDEA {idx}: {idea.get('title', 'Untitled')}")
        lines.append(f"Context : {idea.get('context', 'N/A')}")
        lines.append(f"Angle   : {idea.get('angle', 'N/A')}")
        lines.append(f"Source  : {idea.get('source_type', 'N/A').upper()}  |  Region: {idea.get('region', 'N/A')}")
        lines.append("-" * 50)
    return "\n".join(lines)

def get_doc_size(service, doc_id):
    doc = service.documents().get(documentId=doc_id).execute()
    content = doc.get("body", {}).get("content", [])
    end_index = content[-1].get("endIndex", 1) if content else 1
    return doc, end_index

def trim_doc_if_needed(service, doc_id, doc_label):
    doc, end_index = get_doc_size(service, doc_id)
    if end_index <= DOC_SIZE_LIMIT: return
    delete_from = TRIM_TARGET
    delete_to = end_index - 1
    if delete_to <= delete_from: return
    service.documents().batchUpdate(
        documentId=doc_id,
        body={"requests": [{"deleteContentRange": {"range": {"startIndex": delete_from, "endIndex": delete_to}}}]}
    ).execute()

def _prepend_to_doc(service, doc_id, title_text, body_text):
    full_text = f"{title_text}\n\n{body_text}\n\n"
    service.documents().batchUpdate(
        documentId=doc_id,
        body={"requests": [{"insertText": {"location": {"index": 1}, "text": full_text}}]}
    ).execute()

    title_start = 1
    title_end = title_start + utf16_len(title_text)
    body_start = title_start + utf16_len(title_text + "\n\n")
    body_end = title_start + utf16_len(full_text) - 1

    service.documents().batchUpdate(
        documentId=doc_id,
        body={"requests": [
            {
                "updateTextStyle": {
                    "range": {"startIndex": title_start, "endIndex": title_end},
                    "textStyle": {"bold": True, "fontSize": {"magnitude": 18, "unit": "PT"}},
                    "fields": "bold,fontSize"
                }
            },
            {
                "updateTextStyle": {
                    "range": {"startIndex": body_start, "endIndex": body_end},
                    "textStyle": {"bold": False, "fontSize": {"magnitude": 11, "unit": "PT"}},
                    "fields": "bold,fontSize"
                }
            }
        ]}
    ).execute()

def append_to_google_doc(ideas_list, doc_id, label, title_prefix):
    if not ideas_list: return
    creds = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_JSON)
    service = build('docs', 'v1', credentials=creds)
    sydney_tz = pytz.timezone("Australia/Sydney")
    today_str = datetime.now(sydney_tz).strftime("%Y-%m-%d")

    trim_doc_if_needed(service, doc_id, label)

    unique_items = list(dict.fromkeys(ideas_list))
    body_text = "\n\n".join(f"{idx}. {item}" for idx, item in enumerate(unique_items, 1))

    _prepend_to_doc(service, doc_id, f"{title_prefix} for {today_str}", body_text)
    print(f"✅ Prepended {len(unique_items)} items to {label}.")

def _load_log_file(path):
    """Load a JSON log file, returning [] if missing or empty/corrupt."""
    if not os.path.exists(path):
        return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            return json.loads(content) if content else []
    except (json.JSONDecodeError, ValueError):
        print(f"  ⚠️ Log file {path} was empty or corrupt — starting fresh.")
        return []

def save_to_logs(all_ideas_structured, all_posts):
    date_str = datetime.now().strftime("%Y-%m-%d")

    # Save Ideas (structured dicts — clean for webapp rendering)
    if all_ideas_structured:
        os.makedirs('web/logs/ideas', exist_ok=True)
        ideas_file = f"web/logs/ideas/{date_str}.json"
        log_data = {"timestamp": datetime.now().isoformat(), "ideas": all_ideas_structured}
        existing = _load_log_file(ideas_file)
        existing.append(log_data)
        with open(ideas_file, 'w', encoding='utf-8') as f:
            json.dump(existing, f, indent=4)
        print(f"✅ Ideas logged to {ideas_file}")

    # Save Posts (plain text strings)
    if all_posts:
        os.makedirs('web/logs/posts', exist_ok=True)
        posts_file = f"web/logs/posts/{date_str}.json"
        log_data = {"timestamp": datetime.now().isoformat(), "posts": all_posts}
        existing = _load_log_file(posts_file)
        existing.append(log_data)
        with open(posts_file, 'w', encoding='utf-8') as f:
            json.dump(existing, f, indent=4)
        print(f"✅ Posts logged to {posts_file}")

if __name__ == "__main__":
    print("="*50)
    print("VITTI CAPITAL - Ideas & LinkedIn Post Generator")
    print("="*50)

    MAX_IDEAS = 15
    MAX_POSTS = 5

    # 1. Fetch Raindrop Bookmarks
    bookmarks = fetch_raindrop_bookmarks()
    print(f"\n📌 Found {len(bookmarks)} unused Raindrop bookmarks.")

    # 2. Branch: bookmarks exist → hybrid; no bookmarks → news only
    if bookmarks:
        needed = max(0, 5 - len(bookmarks))
        if needed > 0:
            print(f"⚙️  Supplementing with {needed} AU financial news topics from web...")
            web_topics = fetch_web_ideas(needed)
            for t in web_topics:
                t['source_type'] = 'news'
            bookmarks.extend(web_topics)
        for bm in bookmarks:
            if 'source_type' not in bm:
                bm['source_type'] = 'raindrop'
        print(f"📋 Total sources to process: {len(bookmarks)} (raindrop + news hybrid)")
    else:
        print("⚙️  No bookmarks found. Fetching AU financial news only...")
        bookmarks = fetch_web_ideas(7)
        for bm in bookmarks:
            bm['source_type'] = 'news'
        print(f"📋 {len(bookmarks)} news topics fetched.")

    if not bookmarks:
        print("❌ No real context available. Exiting — no filler will be generated.")
        exit(0)

    all_ideas_structured, all_ideas_str, used_ids = [], [], []

    # 3. Generate and filter ideas from each source
    for bm in bookmarks:
        if len(all_ideas_structured) >= MAX_IDEAS:
            break
        print(f"\n💡 Generating ideas for: {bm.get('title', 'Unknown')[:70]}")
        raw = generate_ideas(bm)
        filtered = parse_and_filter_ideas(raw)
        print(f"   ✅ {len(filtered)} idea(s) passed quality filter.")
        all_ideas_structured.extend(filtered)
        if raw:
            all_ideas_str.append(raw)
        if "id" in bm:
            used_ids.append(bm["id"])

    all_ideas_structured = all_ideas_structured[:MAX_IDEAS]
    print(f"\n📊 Total ideas after filtering: {len(all_ideas_structured)} (max {MAX_IDEAS})")

    if not all_ideas_structured:
        print("❌ No ideas passed the quality filter. Exiting — nothing will be written to docs.")
        exit(0)

    # 4. Generate LinkedIn posts from top ideas (3–5 max)
    top_ideas = all_ideas_structured[:MAX_POSTS]
    all_posts = []
    print(f"\n✍️  Generating LinkedIn posts for top {len(top_ideas)} idea(s)...")
    for idea in top_ideas:
        print(f"   📝 Post for: {idea.get('title', '')[:70]}")
        post = generate_linkedin_post(idea)
        if post:
            all_posts.append(post)
        else:
            print("   ↩ Skipped (weak or no content).")

    print(f"\n📊 Posts generated: {len(all_posts)} (max {MAX_POSTS})")

    # 5. Save ideas as readable text and posts to Google Docs
    ideas_doc_text = format_ideas_for_doc(all_ideas_structured)
    if ideas_doc_text:
        append_to_google_doc([ideas_doc_text], GOOGLE_DOC_ID, "Ideas Doc", "Ideas")
    if all_posts:
        append_to_google_doc(all_posts, NEW_GOOGLE_DOC_ID, "LinkedIn Posts Doc", "LinkedIn Posts")

    # 6. Log and mark used bookmarks
    save_to_logs(all_ideas_structured, all_posts)
    for bm_id in used_ids:
        mark_bookmark_used(bm_id)

    print("\n✅ Completed VITTI Ideas & LinkedIn Pipeline!")
