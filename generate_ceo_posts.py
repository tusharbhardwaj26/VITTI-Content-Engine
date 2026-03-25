import os
import requests
import json
import re
from datetime import datetime, timezone
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import pytz
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_MODEL = "sonar-pro"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_FALLBACK_MODEL = "llama-3.1-8b-instant"
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON", "vitti-ideas-e5256b131985.json")
CEO_LINKEDIN_DOC_ID = os.getenv("CEO_LINKEDIN_DOC_ID")

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

def extract_first_json_array(text):
    """Extract the first complete JSON array of objects or a single JSON object from a string."""
    original_text = text
    text = text.replace("```json", "").replace("```", "").strip()
    
    # Strategy 1: Find every occurrence of '[' (arrays)
    for match in re.finditer(r'\[', text):
        start = match.start()
        after_bracket = text[start+1:].lstrip()
        # Peek ahead: skip citations like [1], but allow objects [{
        if not after_bracket or not after_bracket.startswith('{'):
            continue
            
        depth = 0
        for i, ch in enumerate(text[start:], start):
            if ch == '[':
                depth += 1
            elif ch == ']':
                depth -= 1
                if depth == 0:
                    return text[start:i+1]
    
    # Strategy 2: If no array was found, search for a top-level JSON object '{ ... }'
    for match in re.finditer(r'\{', text):
        start = match.start()
        depth = 0
        for i, ch in enumerate(text[start:], start):
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    return text[start:i+1]

    # Debug: If still nothing, show the response prefix
    print(f"  ⚠️ Extraction failed. Response started with: {original_text[:100]}...")
    return None

def fetch_latest_financial_news():
    for attempt in range(1, 4):
        print(f"🔍 Fetching latest Australian financial news (Attempt {attempt}/3)...")
        prompt = """Search the web RIGHT NOW and retrieve exactly 10 of the most significant real financial news stories published in the last 24-48 hours.

        STRICT REQUIREMENTS - each story MUST:
        - Be real, verifiable, and published very recently (not older than 48 hours)
        - Include at least ONE specific number: percentage move, dollar amount, market cap, volume, basis points, etc.
        - Name at least ONE real entity: company (ASX ticker preferred), city, sector, fund, or person
        - Be in one of these categories ONLY:
            * ASX stock/sector movements
            * Australian real estate market data
            * M&A, PE, VC deals in Australia or globally significant
            * Australian macro economy (RBA, inflation, GDP, employment)
            * Global commodities affecting Australia (iron ore, gold, coal, lithium)

        REJECT any story that:
        - Has no specific numbers
        - Is vague or opinion-based without data
        - Is motivational or lifestyle content
        - Is older than 48 hours

        OUTPUT: STRICT RAW JSON ARRAY ONLY. NO MARKDOWN. NO PREAMBLE.
        Format: [{"headline": "...", "facts": "specific numbers and named entities here", "relevance": "why this matters to institutional investors"}]
        """

        url = "https://api.perplexity.ai/chat/completions"
        headers = {"Authorization": f"Bearer {PERPLEXITY_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": PERPLEXITY_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1, "max_tokens": 4000
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=90)
            if response.status_code != 200:
                print(f"  ⚠️ Attempt {attempt} failed (Status {response.status_code})")
                continue

            content = response.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            json_str = extract_first_json_array(content)
            if json_str:
                try:
                    data = json.loads(json_str)
                    if data:
                        return data
                except Exception:
                    pass
            print(f"  ⚠️ Attempt {attempt} returned unparseable content. Retrying...")
        except Exception as e:
            print(f"  ⚠️ Attempt {attempt} error: {e}")
            
    print("❌ All 3 attempts to fetch news failed. Returning empty.")
    return []

def is_news_item_strong(item):
    """Quality gate: skip items with no numbers or no named entities."""
    facts = item.get('facts', '') + ' ' + item.get('headline', '')
    has_number = bool(re.search(r'[\d]+[%$.,]?[\d]*[%MBKbmk]?', facts))
    # Must have at least one named entity signal: uppercase word, ASX ticker, or city
    has_entity = bool(re.search(r'[A-Z]{2,}', facts))
    if not has_number:
        print(f"  ⚠️ SKIPPED (no numbers): {item.get('headline', '')[:60]}")
    if not has_entity:
        print(f"  ⚠️ SKIPPED (no entities): {item.get('headline', '')[:60]}")
    return has_number and has_entity

def _call_groq(prompt, temperature=0.7, model=GROQ_MODEL):
    if not groq_client:
        print("❌ GROQ_API_KEY is missing!")
        return ""
    try:
        completion = groq_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=4000
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        err_msg = str(e)
        if "rate_limit_exceeded" in err_msg.lower() and model != GROQ_FALLBACK_MODEL:
            print(f"  ⚠️ Groq Rate Limit (429) on {model}. Falling back to {GROQ_FALLBACK_MODEL}...")
            return _call_groq(prompt, temperature, model=GROQ_FALLBACK_MODEL)
        print(f"❌ Groq Error: {e}")
        return ""

def generate_ceo_linkedin_post(news_item):
    context_info = f"Headline: {news_item.get('headline')}\nFacts: {news_item.get('facts')}\nRelevance: {news_item.get('relevance')}"

    prompt = f"""You are writing a LinkedIn post for Shubham Goyal, Founder and CEO of VITTI Capital (a Sydney-based institutional investment firm).

NEWS/TOPIC:
{context_info}

STRICT RULES — you MUST follow ALL of these or the post will be rejected:
✅ Open with a single bold, unexpected, curiosity-inducing headline (one line, no fluff).
✅ Use the SPECIFIC numbers, company names, and events from the news above — do not invent data.
✅ Provide genuine institutional insight: what does this mean for investors, capital flows, or the sector?
✅ Sound like a real CEO with skin in the game, not a commentator. First-person perspective.
✅ Professional and direct. No motivational platitudes.
✅ End with ONE sharp, open-ended question that forces a response from institutional investors or founders.
✅ 150–250 words. No emojis. No markdown bold (**). No citation markers ([1]).

STRICT REJECT — if the news context is vague or has no real data, respond ONLY with: SKIP
Do NOT invent statistics or name companies not mentioned in the news.

Write the complete post now:"""

    try:
        post = _call_groq(prompt, 0.65)
        post = post.replace("**", "")
        post = re.sub(r'\[\d+\]', '', post)
        if post.strip().upper() == "SKIP" or len(post.strip()) < 80:
            print(f"  ⚠️ GROQ returned SKIP or empty for: {news_item.get('headline', '')[:60]}")
            return ""
        return post
    except Exception as e:
        print(f"⚠️ Error generating post: {e}")
        return ""

def append_to_ceo_doc(posts_with_topics):
    creds = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_JSON)
    service = build('docs', 'v1', credentials=creds)
    
    sydney_tz = pytz.timezone("Australia/Sydney")
    today_str = datetime.now(sydney_tz).strftime("%Y-%m-%d %A")
    
    separator = "=" * 60
    content_parts = [f"LinkedIn Content Generated: {today_str}\n{separator}\n\n"]
    
    for idx, item in enumerate(posts_with_topics, 1):
        content_parts.append(f"POST {idx}: {item['topic']}\n")
        content_parts.append("-" * 50 + "\n\n")
        content_parts.append(f"{item['post']}\n\n")
        content_parts.append(separator + "\n\n")
    
    full_text = "".join(content_parts)
    header_len = len(f"LinkedIn Content Generated: {today_str}")
    
    requests_body = [
        {"insertText": {"location": {"index": 1}, "text": full_text}},
        {
            "updateTextStyle": {
                "range": {"startIndex": 1, "endIndex": 1 + header_len},
                "textStyle": {"bold": True, "fontSize": {"magnitude": 14, "unit": "PT"}},
                "fields": "bold,fontSize"
            }
        }
    ]
    
    service.documents().batchUpdate(documentId=CEO_LINKEDIN_DOC_ID, body={"requests": requests_body}).execute()
    print(f"✅ Appended {len(posts_with_topics)} posts to CEO's LinkedIn Doc")

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

def save_to_logs(posts_with_topics):
    os.makedirs('web/logs/ceo', exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_file = f"web/logs/ceo/{date_str}.json"

    log_data = {"timestamp": datetime.now().isoformat(), "posts": posts_with_topics}
    existing = _load_log_file(log_file)
    existing.append(log_data)

    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(existing, f, indent=4)
    print(f"✅ Logged to {log_file}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("VITTI CAPITAL - CEO LINKEDIN CONTENT GENERATOR")
    print("="*60 + "\n")

    MAX_POSTS = 5
    news_items = fetch_latest_financial_news()

    if not news_items:
        print("❌ No real financial news found. Exiting — no filler will be generated.")
        exit(0)

    print(f"📰 {len(news_items)} news items fetched. Applying quality gate...")
    strong_items = [item for item in news_items if is_news_item_strong(item)]
    print(f"✅ {len(strong_items)} items passed quality gate.")

    if not strong_items:
        print("❌ No news items passed the quality gate. Exiting.")
        exit(0)

    posts_with_topics = []

    for idx, item in enumerate(strong_items, 1):
        if len(posts_with_topics) >= MAX_POSTS:
            break
        topic_title = item.get('headline', f"Topic {idx}")
        print(f"📝 Generating post {len(posts_with_topics)+1}/{MAX_POSTS}: {topic_title[:70]}")
        post = generate_ceo_linkedin_post(item)
        if post:
            posts_with_topics.append({'topic': topic_title, 'post': post})
        else:
            print(f"  ↩ Skipped (weak content returned by GROQ).")

    print(f"\n📊 Result: {len(posts_with_topics)} post(s) generated (target: {MAX_POSTS}).")

    if posts_with_topics:
        append_to_ceo_doc(posts_with_topics)
        save_to_logs(posts_with_topics)
        print("\n✅ COMPLETE! CEO's LinkedIn content is ready.")
    else:
        print("\n❌ No posts passed quality checks. Nothing written to doc.")
