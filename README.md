# AI/ML Monitor 📊

A decoupled daily intelligence dashboard for monitoring frontier AI/ML papers, product launches, and industry news.

## Project Structure

```
ai-monitor/
├── data/
│   ├── manifest.json              # Registry of tracked dates and metadata
│   ├── 2026-10-03.json            # Daily intel payload
│   ├── 2026-10-02.json
│   ├── 2026-10-01.json
│   ├── 2026-09-30.json
│   └── 2026-09-28.json
├── index.html                     # Decoupled frontend viewer (loads data asynchronously)
├── scripts/
│   └── update_monitor.py          # Helper script to ingest daily payload & update manifest
└── README.md
```

## Data Contract Schema

Each daily file `data/YYYY-MM-DD.json` adheres to the following structure:

```json
{
  "date": "YYYY-MM-DD",
  "papers": {
    "LLMs": [
      {
        "title": "Paper Title",
        "author": "Lab / Authors",
        "description": "Concise summary",
        "analogy": "🧠 Intuitive analogy",
        "links": [
          { "text": "Paper", "url": "https://...", "type": "primary" }
        ]
      }
    ],
    "Vision/Multimodal": [],
    "Agents & Reasoning": [],
    "Infrastructure & Optimization": []
  },
  "launches": [
    {
      "company": "Company Name",
      "name": "Product / Feature Name",
      "description": "Summary of release",
      "links": [
        { "text": "Release", "url": "https://...", "type": "primary" }
      ]
    }
  ],
  "news": [
    {
      "company": "Company / Topic",
      "headline": "Headline summary",
      "links": [
        { "text": "Source", "url": "https://...", "type": "primary" }
      ]
    }
  ]
}
```

## Running the Dashboard

To view the dashboard locally with dynamic JSON fetching:

```bash
cd /Users/diegoferrua/.gemini/antigravity/scratch/ai-monitor
python3 -m http.server 8000
```

Open `http://localhost:8000` in your web browser.

## Ingesting New Intel

Use `scripts/update_monitor.py` to ingest a new day:

```bash
# Ingest via JSON file
python3 scripts/update_monitor.py --date 2026-10-04 --file payload.json

# Ingest via inline JSON
python3 scripts/update_monitor.py --date 2026-10-04 --json '{"date":"2026-10-04", "papers": {...}, "launches": [], "news": []}'

# Ingest via stdin
cat payload.json | python3 scripts/update_monitor.py --date 2026-10-04
```
