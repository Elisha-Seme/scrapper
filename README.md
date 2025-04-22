# 🌍 YOMA Categorized Opportunities Scraper

## 📋 Description

The **YOMA Categorized Opportunities Scraper** is a Python tool that automatically searches and extracts current youth opportunities (like internships, scholarships, jobs, grants) using Google Search and AI-powered summarization. The script:

- Uses the Google Search API to find links by category
- Extracts full article content from each link (like a human, not using selectors)
- Sends the content to Groq/ChatGPT to extract structured data
- Filters for only relevant and current (2025+) opportunities
- Saves the result in a downloadable CSV file
- Generates short, styled summaries perfect for social media
- Produces a categorized PDF and `.txt` version for sharing or archiving

Supported categories include:
- Scholarships
- Internships
- Jobs
- Grants
- Competitions
- Workshops
- Fellowships
- Training
- Conferences
- Exchange Programs
- Volunteering
- Research
- Agriculture
- AI & Data Science
- Business & Entrepreneurship
- Career Development
- Creative Industry
- Environment & Climate
- Technology & Digitization
- Tourism & Hospitality

---

## 🧰 Dependencies

Install the required libraries using pip:

```bash
pip install requests beautifulsoup4 googlesearch-python pymupdf reportlab tiktoken openai pandas
```

If you're using Groq for summarization, ensure you also set your Groq API key in your environment variables.

---

## ⚙️ How It Works

1. **Search Generation**:  
   ChatGPT/Groq generates targeted Google search queries per opportunity category.

2. **Scraping**:  
   The script searches Google using the generated queries, then visits each result and extracts the full readable text (ignoring HTML noise).

3. **Summarization**:  
   Full article content is sent to Groq/ChatGPT to:
   - Detect the title, type, location, start/end dates
   - Extract the opportunity description
   - Create a 100–150 character summary post with hashtags and emojis

4. **Filtering & Formatting**:
   - Past or duplicate opportunities are removed
   - Summaries outside the required length range are excluded
   - Descriptions are trimmed to max 2000 characters
   - Hidden column shows "Yes"/"No"
   - 'ParticipantLimit' is renamed to 'Participants'

5. **Output**:
   - CSV with cleaned, categorized data
   - PDF categorized by type for printing/distribution
   - TXT file with styled social media-ready blurbs

---

## 🖥️ Running the Script

```bash
python scraper.py
```

Make sure your API keys (Groq or OpenAI) are properly configured in your environment.
---


