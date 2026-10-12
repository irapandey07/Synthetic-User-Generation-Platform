# Technical Documentation — Synthetic User Research Agent

## 1. Overview

This system simulates user research using AI-generated synthetic personas.
It is composed of 7 backend agents exposed as REST endpoints, and a React
frontend that orchestrates them into a single research workflow: generate
personas → simulate responses (survey / interview / live chat) → extract
insights → score adoption → export a report.

## 2. Architecture

```
┌─────────────────────┐         HTTP (JSON)        ┌──────────────────────────┐
│   React frontend      │  ───────────────────────▶  │   Flask backend            │
│   (Vite, port 5173)   │  ◀───────────────────────  │   (port 3001)              │
└─────────────────────┘                             └──────────────────────────┘
                                                                  │
                                                                  ▼
                                                     ┌──────────────────────────┐
                                                     │  USE_MOCK toggle          │
                                                     │  ├─ true: local Python    │
                                                     │  │   random generators    │
                                                     │  └─ false: Anthropic      │
                                                     │      Claude API calls     │
                                                     └──────────────────────────┘
```

The frontend never calls Claude directly — every request goes through the
Flask backend, which decides whether to answer with a free local mock
generator or a real Claude API call, based on the `USE_MOCK` environment
variable. This keeps the API key server-side only and makes the whole app
runnable and demoable with zero cost.

## 3. Agents and endpoints

| # | Agent | Endpoint | Role |
|---|---|---|---|
| 1 | Persona Generation | `POST /api/generate-personas` | Builds N synthetic personas from a product/audience/objective brief. Chunks requests into batches of 20 for large counts (up to 100). |
| 2 | Survey Simulation | `POST /api/simulate-survey` | Runs personas through the research objective (plus optional custom questions) for a closed-choice stance + aggregate breakdown. |
| 3 | Interview Simulation | `POST /api/simulate-interview` | Answers a batch of open-ended questions per persona, plus cross-persona themes. |
| 4 | Interview Chat | `POST /api/interview-chat` | Live, turn-by-turn conversation with one persona. Conversation history is passed on every request (the backend is stateless) so the model sees full context each turn. |
| 5 | Insight Extraction | `POST /api/extract-insights` | Analyzes accumulated survey/interview data for themes, sentiment, agreement patterns, behavioral trends. |
| 6 | Adoption Scoring | `POST /api/score-adoption` | Segments personas by tech-savviness and scores likely adoption (0–100) with reasoning per segment. |
| 7 | Report Generation | `POST /api/generate-report` | Compiles all of the above into a downloadable PDF via `reportlab`. |

## 4. Data model

A persona object:
```json
{
  "id": "P-0001",
  "name": "string",
  "age": 0,
  "occupation": "string",
  "location": "string",
  "quote": "string",
  "personalityTraits": [{ "trait": "string", "score": 0 }],
  "behavioralPatterns": ["string"],
  "psychProfile": "string",
  "painPoints": ["string"],
  "techSavviness": "Low | Medium | High"
}
```

Every simulation/analysis endpoint takes an array of these persona objects
(plus the original brief) and returns structured JSON specific to that
agent — see each function's docstring in `backend/app.py` for its exact
schema.

## 5. Design decisions worth noting

- **Mock/real toggle instead of always calling the API.** This is a
  deliberate engineering choice, not a shortcut — it lets the whole
  pipeline be tested and demoed without an API key or billing, while
  still supporting genuinely reasoned output when a real key is supplied.
- **Chunked persona generation.** A single request for 100 personas risks
  exceeding the model's response token limit or timing out. Generating in
  batches of 20 and combining results avoids both failure modes.
- **Stateless chat history.** `/api/interview-chat` doesn't store
  conversation state server-side; the frontend sends the full history each
  turn. This keeps the backend simple (no session/database) at the cost
  of slightly larger requests as a conversation grows.

## 6. Known limitations

- Nothing persists between page reloads — all state lives in React memory.
- Mock mode uses randomized templates, not real reasoning; it is a
  free testing aid, not a substitute for real API output.
- Insight quality (Milestone 4, item 3) has not been formally validated
  across varied scenarios — this requires manual review by a person
  across multiple test runs, which is a testing/QA task rather than a
  feature that can be automated away.
