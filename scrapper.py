import random
import requests
import csv
import json
from datetime import datetime, timedelta
from trafilatura import fetch_url, extract
from time import sleep
import os

# Config
GOOGLE_API_KEY = 'AIzaSyAnWAKuT1wGErj16dmwDSEAh9S52UVNgmI'
CSE_ID = '4112369310dd04fa3'
GROQ_API_KEY = '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'
NUM_RESULTS = 5

categories = [
    "AI, Data and Analysis", "Career & Personal Development", "Business & Entrepreneurship", "Creative Industry and Arts",
    "Agriculture", "Environment and Climate", "Technology and Hopspitality", "Other"
]

additional_keywords = [
    "free courses", "scholarships", "internship", "fellowship", "grants",
    "youth programs", "volunteering", "research opportunities", "training programs"
]

BASE_QUERY = 'youth opportunities site:.org OR site:.gov OR site:.edu Kenya 2025'

def generate_search_query(category_choice, selected_keywords):
    """Generate search query using Groq based on selected categories and keywords"""
    system_prompt = """
    You are a search query generator for Kenyan youth opportunities. Create a Google search query based on the provided category and keywords.
    
    Rules:
    1. Focus on opportunities in Kenya
    2. MUST include the year 2025 using multiple techniques (e.g., "2025", "year 2025", "for 2025")
    3. Use site:.org OR site:.gov OR site:.edu to limit to authoritative sources
    4. Include 2-3 relevant opportunity types (internship, fellowship, grant, etc.)
    5. Use Google search operators (intext:2025, intitle:2025) to find 2025-specific content
    6. Keep it concise (under 20 words)
    7. Return ONLY the query string, no explanations or markdown
    """
    
    user_prompt = f"Category: {category_choice}\nKeywords: {', '.join(selected_keywords)}"
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "model": "gemma2-9b-it",
        "temperature": 0.5
    }

    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions",
                                headers=headers, json=data)
        response.raise_for_status()
        query = response.json()["choices"][0]["message"]["content"].strip()
        if "2025" not in query:
            query = query + " 2025 intitle:2025 OR intext:2025"
        return query if query else BASE_QUERY
    except requests.exceptions.RequestException:
        return BASE_QUERY

def google_search(query, api_key, cse_id, num_results):
    search_results = []
    start = 1
    while len(search_results) < num_results:
        url = f'https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cse_id}&start={start}'
        response = requests.get(url)
        data = response.json()
        if 'items' not in data:
            break
        for item in data['items']:
            link = item['link']
            if any(x in link for x in ['wikipedia.org', 'medium.com', 'blog', 'com']):
                continue
            if link not in search_results:
                search_results.append(link)
            if len(search_results) >= num_results:
                break
        start += 10
        sleep(1)
    return search_results

def extract_text_from_links(links):
    results = []
    for link in links:
        html = fetch_url(link)
        if html:
            text = extract(html, include_comments=False, include_tables=False)
            if text and len(text.split()) > 100:
                results.append({'url': link, 'content': text[:2990]})
        sleep(1)
    return results[:5]

def build_combined_payload(extracted_data):
    combined = ""
    for i, item in enumerate(extracted_data):
        combined += f"Opportunity {i+1}:\nURL: {item['url']}\nContent:\n{item['content']}\n\n"
    return combined

def ask_groq_structured_data(content, category):
    system_prompt = f"""
    You are a professional data extractor. Extract structured details from this {category} opportunity.

    Extract and return a JSON list of structured opportunities in this format:
    "Title": "", "Type": "", "Engagement": "", "Categories": "", "Link": "", "Summary": "", "Description": "", "Languages": "", "Location": "", "Difficulty": "", "EffortCount": 0, "EffortInterval": "", "DateStart": "", "DateEnd": "", "ParticipantLimit": null, "ZltoReward": 0, "ZltoRewardPool": 0, "Skills": "", "Keywords": "", "Hidden": "No", "ExternalId": ""

    STRICT FORMAT REQUIREMENTS:
    - Type: rewrite "{category.title()}" to a better title,
    - Summary: Rewrite to be social media ready, exactly 150 chars. Add 2-3 emojis placed intelligently in the middle and end (NOT at the beginning). Choose emojis from: 🚀, ✨, 📚, 💼, 🌟, 🔍, 💡, 🌍, 🎓, 🌱, 🤝, 💻, 🔬, 🎯, 📊
    - Description: Rewrite and cap at exactly 2000 chars. Add 3-5 emojis placed intelligently in the middle and end (NOT at the beginning). Use emojis from: 🚀, ✨, 📚, 💼, 🌟, 🔍, 💡, 🌍, 🎓, 🌱, 🤝, 💻, 🔬, 🎯, 📊
    - Engagement: "Online", "Offline", or "Hybrid"
    - Categories: Only choose from: "AI & Data Science", "Career Development", "Business", "Health/Medicine", "Tourism", "Environmental", "Technology", or "Other",
    - DateStart: analyze the content and return in MM/DD/YYYY format (e.g. 04/16/2025),
    - DateEnd: analyze the content and return in MM/DD/YYYY format (e.g. 06/30/2025),
    - Hidden: "No",
    - ZltoReward and ZltoRewardPool: 0,
    - Languages: "EN",
    - Location: Guess (default "Kenya"),
    - Difficulty: "Beginner", "Intermediate", "Advanced", or "Any",
    - EffortCount: realistic guess, vary values,
    - EffortInterval: "Minutes", "Hours", "Days", or "Weeks",
    - ParticipantLimit: set null if not specified, otherwise random number between 10-500,
    - Skills: 2-5 comma-separated,
    - Keywords: 5-7 comma-separated,
    - ExternalId: 8-char uppercase ID based on title,
    - Return ONLY VALID JSON. No markdown or explanations.
    """

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content}
        ],
        "model": "gemma2-9b-it",
        "temperature": 0.2
    }

    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions",
                                headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return {}

def save_to_csv(json_data):
    if not json_data or "choices" not in json_data:
        print("No valid Groq response.")
        return

    content = json_data["choices"][0]["message"]["content"]
    try:
        parsed = json.loads(content) if isinstance(content, str) else content
    except Exception as e:
        print("Error parsing JSON from Groq:", e)
        return

    # Emoji pool for post-processing if needed
    emoji_pool = ['🚀', '✨', '📚', '💼', '🌟', '🔍', '💡', '🌍', '🎓', '🌱', '🤝', '💻', '🔬', '🎯', '📊']

    if isinstance(parsed, list) and parsed:
        headers = parsed[0].keys()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'opportunities_{timestamp}.csv'
        
        # Get current date for default start date
        current_date = datetime.now()
        current_date_str = current_date.strftime("%m/%d/%Y")
        
        # Track used end dates to ensure uniqueness
        used_end_dates = set()

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for idx, row in enumerate(parsed):
                # ALWAYS set DateStart to current date regardless of what was found
                if row.get('DateStart') and row['DateStart'] not in ("", None, "N/A"):
                    print(f"Opportunity {idx+1}: Found start date: {row['DateStart']} but using current date instead: {current_date_str}")
                else:
                    print(f"Opportunity {idx+1}: No start date found. Using current date: {current_date_str}")
                    
                # Always set to current date
                row['DateStart'] = current_date_str
                
                # Process DateEnd
                end_date_found = False
                if row.get('DateEnd') and row['DateEnd'] not in ("", None, "N/A"):
                    try:
                        # Try to parse the date
                        for fmt in ("%m/%d/%Y", "%d-%b-%Y", "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
                            try:
                                date_obj = datetime.strptime(row['DateEnd'], fmt)
                                # Ensure date is after current date
                                if date_obj > current_date:
                                    row['DateEnd'] = date_obj.strftime("%m/%d/%Y")
                                    print(f"Opportunity {idx+1}: Found valid end date: {row['DateEnd']}")
                                    end_date_found = True
                                    break
                                else:
                                    # Date is not after current date, will generate random one
                                    raise ValueError("End date must be after current date")
                            except ValueError:
                                continue
                    except Exception:
                        pass
                
                # If no valid end date was found or processed
                if not end_date_found:
                    # Generate random end date between 6 months and 2 years from current date
                    while True:
                        days_to_add = random.randint(180, 730)  # 6 months to 2 years
                        end_date = current_date + timedelta(days=days_to_add)
                        end_date_str = end_date.strftime("%m/%d/%Y")
                        
                        # Ensure it's unique
                        if end_date_str not in used_end_dates:
                            used_end_dates.add(end_date_str)
                            break
                        # If we somehow tried all possible dates (very unlikely), add a small random offset
                        days_to_add += random.randint(1, 10)
                    
                    row['DateEnd'] = end_date_str
                    print(f"Opportunity {idx+1}: Generated random end date: {row['DateEnd']} (6 months to 2 years from now)")
                
                # Ensure summary is capped at 150 chars and has emojis
                if 'Summary' in row:
                    summary = row['Summary']
                    # Remove existing emojis for clean processing if any
                    for emoji in emoji_pool:
                        summary = summary.replace(emoji, "")
                    # Cap at ~140 chars to leave room for emojis
                    summary = summary[:140].strip()
                    # Add emojis in middle and end if not already present
                    mid_point = len(summary) // 2
                    emoji1 = random.choice(emoji_pool)
                    emoji2 = random.choice(emoji_pool)
                    while emoji2 == emoji1:
                        emoji2 = random.choice(emoji_pool)
                    summary = f"{summary[:mid_point]} {emoji1} {summary[mid_point:]} {emoji2}"
                    # Ensure final length is 150 or less
                    row['Summary'] = summary[:150]
                
                # Ensure description is capped at 2000 chars and has emojis
                if 'Description' in row:
                    desc = row['Description']
                    # Remove existing emojis for clean processing if any
                    for emoji in emoji_pool:
                        desc = desc.replace(emoji, "")
                    # Cap at -1980 chars to leave room for emojis
                    desc = desc[:1980].strip()
                    # Add 3-5 emojis distributed in middle and end
                    num_emojis = random.randint(3, 5)
                    segments = num_emojis + 1
                    segment_length = len(desc) // segments
                    result_desc = ""
                    for i in range(segments - 1):
                        segment = desc[i*segment_length:(i+1)*segment_length]
                        emoji = random.choice(emoji_pool)
                        result_desc += segment + f" {emoji} "
                    result_desc += desc[(segments-1)*segment_length:]
                    emoji_final = random.choice(emoji_pool)
                    result_desc += f" {emoji_final}"
                    # Ensure final length is 2000 or less
                    row['Description'] = result_desc[:2000]
                
                # Fill in other missing fields
                for key in headers:
                    if key not in row or row[key] in ("", None):
                        if key == "ParticipantLimit":
                            row[key] = None if random.random() < 0.5 else random.randint(10, 500)
                        elif key in ("ZltoReward", "ZltoRewardPool", "EffortCount"):
                            row[key] = 0
                        else:
                            row[key] = "N/A"
                
                writer.writerow(row)

        print(f"✅ Saved {len(parsed)} opportunities to {filename}")
    else:
        print("⚠️ Groq response didn't return a valid list.")

def main():
    print("Choose a category:")
    for idx, category in enumerate(categories, 1):
        print(f"{idx}. {category}")

    try:
        category_choice = int(input("Enter number: "))
        category_choice = categories[category_choice - 1]
    except (ValueError, IndexError):
        print("Invalid. Defaulting to 'AI & Data Science'.")
        category_choice = "AI & Data Science"

    print("Choose 2 keywords:")
    for idx, keyword in enumerate(additional_keywords, 1):
        print(f"{idx}. {keyword}")

    try:
        first_kw = int(input("Enter number for first keyword: "))
        second_kw = int(input("Enter number for second keyword: "))
        selected_keywords = [additional_keywords[first_kw - 1], additional_keywords[second_kw - 1]]
    except (ValueError, IndexError):
        selected_keywords = ["free courses", "internship"]

    # Generate search query using Groq
    query = generate_search_query(category_choice, selected_keywords)
    print(f"🔍 Generated search query: {query}")

    links = google_search(query, GOOGLE_API_KEY, CSE_ID, NUM_RESULTS)
    print(f"🔗 Found {len(links)} links.")

    extracted = extract_text_from_links(links)
    print(f"📄 Extracted content from {len(extracted)} link(s).")

    if extracted:
        combined_payload = build_combined_payload(extracted)
        groq_response = ask_groq_structured_data(combined_payload, category_choice)
        if groq_response:
            save_to_csv(groq_response)
        else:
            print("❌ No valid response from Groq.")

if __name__ == "__main__":
    main()
