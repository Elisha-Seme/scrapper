
---

# 🧠 Kenyan Youth Opportunities Finder (2025 Edition)

This Python script is designed to help discover and extract **structured data about youth opportunities in Kenya for 2025**, such as **internships, fellowships, scholarships, grants**, and more. It leverages Google Custom Search, full-page content extraction, and Groq AI to intelligently return enriched, CSV-ready opportunity data.

---

## 🔧 Features

- ✅ Auto-generates **smart Google search queries** using Groq AI
- 🔎 Searches authoritative sites (`.org`, `.gov`, `.edu`) for relevant links
- 🧠 Extracts **full article content** (not just snippets)
- 📊 Sends combined content to Groq for structured data extraction
- 🧾 Saves enhanced CSV files with:
  - Cleaned, deduplicated content
  - Accurate, future `DateEnd` values
  - Social media–ready summaries with emojis
  - Auto-inferred skills, difficulty, effort, and more

---

## 📁 Folder Contents

- `opportunities_*.csv`: Output CSV files with structured opportunity data
- `main.py`: The main script file (your current code)

---

## 🧪 How It Works (Pipeline)

1. **User selects a category and keyword(s)**
2. Groq generates a Google query (with filters and 2025-specific operators)
3. Script searches Google via **Custom Search API**
4. Filters useful links, fetches their full content via `trafilatura`
5. Bundles content and sends it to Groq AI for **structured parsing**
6. Saves results into a clean, enriched `.csv`

---

## ⚙️ Configuration

Update your API keys before running:

```python
GOOGLE_API_KEY = 'your-google-api-key'
CSE_ID = 'your-custom-search-engine-id'
GROQ_API_KEY = 'your-groq-api-key'
```

You can configure the number of results with:

```python
NUM_RESULTS = 5  # Number of links to fetch per run
```

---

## 📌 Requirements

Install dependencies:

```bash
pip install requests trafilatura
```

---

## 🚀 Running the Script

Run it directly:

```bash
python main.py
```

Note: For now, category and keyword selections are hardcoded or to be manually set in the script.

---

## 🧠 AI-Powered Smart Features

- Uses **Groq (gemma2-9b-it)** for:
  - Search query generation
  - Opportunity content extraction and classification
- Adds:
  - Dates (auto-inferred and validated)
  - Social-friendly `Summary` field (with 2 emojis)
  - Descriptions (emoji-enhanced, capped at 2000 chars)
  - Smart guesses for skills, difficulty, engagement, etc.

---

## 📝 Output Format

Each row in the CSV contains:

- Title, Type, Description, Summary (social-ready)
- Location, Language, Skills, Difficulty
- Dates (`DateStart`, `DateEnd`)
- Category, Keywords, Engagement Type
- ZltoReward fields, Hidden status, External ID
- And more…

---

## 🛠️ Customization Tips

- Change or add to the categories/keywords list
- Adjust the emoji pool if needed
- Tweak `NUM_RESULTS` for more or fewer results per run
- Integrate into a frontend, LMS, or app

---

## 📥 Example Use Case

Ideal for organizations building:

- Youth opportunity dashboards
- Scholarship aggregators
- Training and upskilling portals
- Social content automation tools

---

## 📬 Credits

- Google Custom Search API
- [Trafilatura](https://github.com/adbar/trafilatura) for full-content scraping
- [Groq](https://groq.com/) + `gemma2-9b-it` for AI parsing

---

## 🧯 Caution

- Make sure API limits (Google, Groq) are respected
- Not suitable for scraping paywalled or private content
- Emojis in summaries/descriptions are added programmatically—double-check for tone/appropriateness

---
