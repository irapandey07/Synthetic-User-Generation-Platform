# Synthetic User Research — Case File

All four milestones from your whiteboard, combined into one working app: a
persona generation agent, survey/interview simulation, live in-character chat,
insight extraction, adoption scoring, a results dashboard, and a downloadable
PDF research report.

```
persona-agent/
├── backend/              Flask API — 7 agents, all callable from one server
├── frontend/             React (Vite) UI — one continuous workspace
└── TECHNICAL_DOCS.md     Architecture and agent documentation (Milestone 4)
```

## Agents included

| Agent | Endpoint | Milestone |
|---|---|---|
| Persona Generation | /api/generate-personas | 1 |
| Survey Simulation (closed-choice stance) | /api/simulate-survey | 1/2 |
| Interview Simulation (batch, scripted Q&A) | /api/simulate-interview | 1/2 |
| Interview Chat (live, turn-by-turn, in-character) | /api/interview-chat | 3 |
| Insight Extraction (themes, sentiment, patterns, trends) | /api/extract-insights | 3 |
| Adoption Scoring (segmented "would use this?" score) | /api/score-adoption | 3 |
| Report Generation (PDF export) | /api/generate-report | 4 |

## Setup

Backend:
    cd backend
    py -m venv venv
    venv\Scripts\activate
    pip install flask flask-cors "anthropic>=0.40.0" python-dotenv reportlab
    copy .env.example .env
    (edit .env, add USE_MOCK=true for free testing)
    python app.py

Frontend (second terminal):
    cd frontend
    npm install
    npm run dev

Open http://localhost:5173

## Milestone 4 usage

1. Generate personas, run survey/interview simulation, extract insights, and
   score adoption as usual.
2. Scroll down to the **Dashboard** — it displays theme clusters, sentiment
   breakdown, key persona quotes, and validation scores in one visual view.
3. Click **Download research report (PDF)** to compile everything into a
   structured PDF, including persona profiles, response highlights, insight
   summary, and validation scoring.
4. Persona count now supports up to 100 — real-mode generation automatically
   splits large batches into chunks of 20 API calls to avoid timeouts.

## On Milestone 4, item 3 and 4

Testing across 100 personas, both simulation modes, and report generation is
something you run and verify yourself — the app now supports it (100-persona
cap, chunked generation), but the testing itself is a QA task, not a feature.
Likewise, the "project report" and "final demonstration" are yours to
prepare — `TECHNICAL_DOCS.md` gives you the architecture write-up to build on.
