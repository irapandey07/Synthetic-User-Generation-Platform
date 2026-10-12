import json
import os
import random
import re

from anthropic import Anthropic
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

MODEL = "claude-sonnet-4-6"

# Free, no-API mock mode. Set USE_MOCK=true in .env (or leave ANTHROPIC_API_KEY
# blank/placeholder) to generate personas locally with random data instead of
# calling Claude. Useful for testing the app end-to-end at zero cost.
USE_MOCK = os.environ.get("USE_MOCK", "").lower() == "true" or not os.environ.get(
    "ANTHROPIC_API_KEY", ""
).startswith("sk-ant-")

FIRST_NAMES = ["Jordan", "Maria", "Tom", "Priya", "Sam", "Linda", "Carlos", "Aisha", "David", "Nina"]
LAST_NAMES = ["Reed", "Alvarez", "Chen", "Patel", "Novak", "Brooks", "Diaz", "Khan", "Foster", "Lund"]
OCCUPATIONS = ["Retired teacher", "Small business owner", "Nurse", "Logistics manager", "Veteran, now consultant", "Accountant", "Retail manager", "Freelance contractor"]
LOCATIONS = ["Columbus, OH", "San Antonio, TX", "Tampa, FL", "Fayetteville, NC", "Phoenix, AZ", "Omaha, NE"]
TRAIT_NAMES = ["Openness", "Price Sensitivity", "Brand Loyalty", "Risk Tolerance", "Trust in Brands", "Tech Adoption"]
BEHAVIORS = ["Reads reviews before buying anything new", "Sticks to routines once satisfied", "Asks friends/family for recommendations", "Compares prices across at least 2-3 stores", "Skeptical of subscription models", "Willing to try samples before committing"]
PAIN_POINTS = ["Distrust of new brands", "Wants a simple, no-fuss setup", "Worried about recurring charges", "Limited time to research options", "Frustrated by a steep learning curve", "Skeptical of subscription pricing", "Wants proof it works before committing", "Concerned about data privacy", "Doesn't want to change an existing routine", "Burned by a similar product before"]
TECH_LEVELS = ["Low", "Medium", "High"]


QUOTE_TEMPLATES = [
    "I'd consider it, but I'd want proof it actually works before I switch from what I use now.",
    "Honestly, if it saves me time I'm in — otherwise it's just another thing to manage.",
    "I've been burned by products that overpromise before, so I go in a little skeptical.",
    "Price matters more to me than features — if it's affordable, I'll give it a shot.",
    "I trust word of mouth more than ads, so I'd ask around before committing.",
    "I'm not against trying new things, I just don't have a lot of patience for a learning curve.",
    "If a friend showed me it working, that'd do more to convince me than any marketing.",
    "I like sticking with what I know, but I'm not totally closed off to switching.",
]

PROFILE_MOTIVATIONS = [
    "driven mainly by trust and proven results rather than novelty",
    "motivated by convenience — anything that saves time or effort wins them over",
    "cautious about recurring costs, weighing price heavily in any decision",
    "influenced strongly by peer recommendations over advertising",
    "resistant to changing existing routines unless the payoff is clear",
    "open to experimenting, especially with low-risk or free trials",
]


def generate_mock_personas(product_description, target_audience, research_objective, count):
    """Builds fake-but-plausible personas locally, no API call, no cost. Each persona
    gets its own randomized quote, age, and psych profile so a batch doesn't read as
    the same person repeated — only shared traits (pain points, behaviors) come from
    a shuffled pool, not a single fixed template."""
    personas = []
    for i in range(count):
        traits = random.sample(TRAIT_NAMES, k=4)
        pain_points = random.sample(PAIN_POINTS, k=2)
        motivation = random.choice(PROFILE_MOTIVATIONS)
        personas.append(
            {
                "id": f"P-{i + 1:04d}",
                "name": f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
                "age": random.randint(20, 65),
                "occupation": random.choice(OCCUPATIONS),
                "location": random.choice(LOCATIONS),
                "quote": random.choice(QUOTE_TEMPLATES),
                "personalityTraits": [
                    {"trait": t, "score": random.randint(20, 90)} for t in traits
                ],
                "behavioralPatterns": random.sample(BEHAVIORS, k=3),
                "psychProfile": (
                    f"A member of the '{target_audience}' segment, {motivation}. "
                    f"Their view of '{product_description}' is shaped by "
                    f"{random.choice(pain_points).lower()} as a recurring concern."
                ),
                "painPoints": pain_points,
                "techSavviness": random.choice(TECH_LEVELS),
            }
        )
    return {"personas": personas}


STANCES = ["Would switch", "Would not switch", "Undecided"]

REASONING_TEMPLATES = {
    "Would switch": [
        "The idea is appealing enough to try once, especially if the first purchase feels low-risk.",
        "Tired of the current option's downsides — willing to switch if it's simple to set up.",
    ],
    "Would not switch": [
        "Comfortable with what's already being used and doesn't see a strong enough reason to change.",
        "Worried about hidden costs or hassle outweighing any benefit.",
    ],
    "Undecided": [
        "Interested in principle but would want to see reviews or try a sample before deciding.",
        "Open to it, but price and convenience would need to be clearer first.",
    ],
}


def generate_mock_survey(personas, product_description, research_objective, questions=None):
    """Simulates how each persona would respond to the research objective, locally."""
    responses = []
    counts = {s: 0 for s in STANCES}
    for p in personas:
        stance = random.choice(STANCES)
        counts[stance] += 1
        response = {
            "personaId": p.get("id"),
            "name": p.get("name"),
            "stance": stance,
            "confidence": random.randint(40, 95),
            "reasoning": random.choice(REASONING_TEMPLATES[stance]),
            "quote": f"Honestly, {REASONING_TEMPLATES[stance][0].lower()}",
        }
        if questions:
            response["answers"] = [
                {"question": q, "answer": random.choice(REASONING_TEMPLATES[stance])}
                for q in questions
            ]
        responses.append(response)
    total = len(personas) or 1
    lead_stance = max(counts, key=counts.get)
    summary = {
        "counts": counts,
        "keyInsight": (
            f"{counts[lead_stance]} of {total} simulated respondents leaned toward "
            f"'{lead_stance.lower()}' regarding \"{product_description}\", relative to the "
            f"objective: {research_objective}"
        ),
    }
    return {"responses": responses, "summary": summary}


def build_survey_prompt(personas, product_description, target_audience, research_objective, questions=None):
    """Builds the instruction prompt for simulating survey responses per persona."""
    persona_summaries = "\n".join(
        f"- {p.get('id')} | {p.get('name')}, {p.get('age')}, {p.get('occupation')}: "
        f"{p.get('psychProfile', '')}"
        for p in personas
    )
    questions_block = ""
    answers_schema = ""
    if questions:
        question_list = "\n".join(f"{i + 1}. {q}" for i, q in enumerate(questions))
        questions_block = f"\n\nSURVEY QUESTIONS (answer each briefly per persona, in addition to the overall stance):\n{question_list}"
        answers_schema = """,
      "answers": [
        { "question": "string", "answer": "string, first person, one sentence" }
      ]"""
    return f"""You are a survey simulation agent. Given these synthetic personas, simulate how
each one would respond to the research objective below, as if they were answering a
short interview question about the product.

PRODUCT DESCRIPTION: {product_description}
TARGET AUDIENCE: {target_audience}
RESEARCH OBJECTIVE: {research_objective}{questions_block}

PERSONAS:
{persona_summaries}

For each persona, decide their stance ("Would switch", "Would not switch", or "Undecided"),
grounded in their psychological profile, and write a short first-person quote and a
one-sentence reasoning explanation.{" If survey questions are listed above, also answer each one briefly per persona." if questions else ""}

Return ONLY valid JSON (no markdown fences, no commentary) matching this exact schema:

{{
  "responses": [
    {{
      "personaId": "P-0001",
      "name": "string",
      "stance": "Would switch" | "Would not switch" | "Undecided",
      "confidence": number (0-100),
      "reasoning": "string, one sentence",
      "quote": "string, first person, one sentence"{answers_schema}
    }}
  ],
  "summary": {{
    "counts": {{ "Would switch": number, "Would not switch": number, "Undecided": number }},
    "keyInsight": "string, 2-3 sentences synthesizing the overall finding relative to the research objective"
  }}
}}"""

DEFAULT_INTERVIEW_QUESTIONS = [
    "Tell me about your current experience with this kind of product — what do you like or dislike?",
    "What would make you consider trying something new here?",
    "What would hold you back from switching?",
]

TAKEAWAY_TEMPLATES = [
    "Open to change but needs proof it actually solves a real problem, not just a nicer pitch.",
    "Values consistency and trust more than novelty — a hard convert.",
    "Price and simplicity matter more than features here.",
    "Word of mouth and reviews carry more weight than advertising for this person.",
]

ANSWER_OPENERS = [
    "Honestly, ",
    "To be real with you, ",
    "I'd say ",
    "Look, ",
    "For me, ",
    "Depends, but ",
]

ANSWER_CORES = [
    "it comes down to whether {product} actually fixes something that's bugging me, like {pain}.",
    "I've been burned before by things that promise a lot and don't deliver, so I'd want proof first.",
    "I'm not against trying {product} if it doesn't add more steps to what I already do.",
    "price matters more to me than the pitch — if it's cheap enough to try, I probably would.",
    "I'd need to hear from someone I trust that it actually works before I bother.",
    "my current setup isn't perfect, but switching feels like extra work I don't have time for.",
    "if it saved me real time, I'd give it a shot — otherwise it's just another app I forget about.",
]


def generate_mock_interview(personas, product_description, research_objective, questions):
    """Simulates a short multi-question interview per persona, locally, no cost.
    Pulls from each persona's own pain points and traits so answers actually differ
    from one persona to the next, instead of reusing one shared template."""
    product_word = product_description.split(" ")[0] if product_description else "it"
    transcripts = []
    for p in personas:
        pain_points = p.get("painPoints") or ["something not working smoothly"]
        qa = []
        for q in questions:
            opener = random.choice(ANSWER_OPENERS)
            core = random.choice(ANSWER_CORES).format(
                product=product_word, pain=random.choice(pain_points).lower()
            )
            qa.append({"question": q, "answer": f"{opener}{core}"})
        transcripts.append(
            {
                "personaId": p.get("id"),
                "name": p.get("name"),
                "qa": qa,
                "takeaway": random.choice(TAKEAWAY_TEMPLATES),
            }
        )
    themes = [
        "Trust and proof-of-results outweigh novelty for most respondents.",
        "Price sensitivity shows up even among otherwise interested respondents.",
        "Word of mouth and peer recommendation matter more than ads.",
    ]
    return {"transcripts": transcripts, "themes": themes}


def build_interview_prompt(personas, product_description, target_audience, research_objective, questions):
    """Builds the instruction prompt for simulating an open-ended interview per persona."""
    persona_summaries = "\n".join(
        f"- {p.get('id')} | {p.get('name')}, {p.get('age')}, {p.get('occupation')}: "
        f"{p.get('psychProfile', '')}"
        for p in personas
    )
    question_list = "\n".join(f"{i + 1}. {q}" for i, q in enumerate(questions))
    return f"""You are an interview simulation agent conducting qualitative research. Given
these synthetic personas, simulate how each one would answer the interview questions
below, in their own first-person voice, grounded in their psychological profile.

PRODUCT DESCRIPTION: {product_description}
TARGET AUDIENCE: {target_audience}
RESEARCH OBJECTIVE: {research_objective}

INTERVIEW QUESTIONS:
{question_list}

PERSONAS:
{persona_summaries}

For each persona, answer every question in 1-2 sentences, first person, in a voice
consistent with their profile. Then write a one-sentence "takeaway" summarizing their
overall stance. Finally, synthesize 3-5 cross-persona themes that emerged.

Return ONLY valid JSON (no markdown fences, no commentary) matching this exact schema:

{{
  "transcripts": [
    {{
      "personaId": "P-0001",
      "name": "string",
      "qa": [
        {{ "question": "string", "answer": "string, first person, 1-2 sentences" }}
      ],
      "takeaway": "string, one sentence"
    }}
  ],
  "themes": ["string", "string", "string"]
}}"""


def build_prompt(product_description, target_audience, research_objective, count):
    """Builds the instruction prompt sent to Claude. Asks for strict JSON so the
    response can be parsed directly into persona cards on the frontend."""
    return f"""You are a synthetic user research agent. Generate {count} diverse, realistic
synthetic personas for a product research study.

PRODUCT DESCRIPTION: {product_description}
TARGET AUDIENCE: {target_audience}
RESEARCH OBJECTIVE: {research_objective}

Requirements:
- Personas must be plausible members of the target audience described above, but diverse
  across age, background, occupation, and outlook within that audience (avoid repeating
  the same archetype).
- Ground every trait and behavior in something relevant to the research objective — this
  is synthetic user research, not generic profile filler.
- Each persona must include a short first-person "quote" that reflects how they'd talk
  about the product/topic in the research objective.

Return ONLY valid JSON (no markdown fences, no commentary) matching this exact schema:

{{
  "personas": [
    {{
      "id": "P-0001",
      "name": "string",
      "age": number,
      "occupation": "string",
      "location": "string",
      "quote": "string, one sentence, first person",
      "personalityTraits": [
        {{ "trait": "string (e.g. Openness)", "score": number (0-100) }}
      ],
      "behavioralPatterns": ["string", "string", "string"],
      "psychProfile": "string, 2-3 sentences describing motivations, decision drivers, and attitude relevant to the research objective",
      "painPoints": ["string", "string"],
      "techSavviness": "Low" | "Medium" | "High"
    }}
  ]
}}

Include exactly 4-6 items in "personalityTraits" per persona (use recognizable traits
such as Openness, Conscientiousness, Risk Tolerance, Trust in Brands, Price Sensitivity,
Tech Adoption — pick whichever are most relevant to the research objective)."""


CHAT_FILLERS = [
    "That's a fair question. Honestly, it comes down to whether it fits my routine without adding hassle.",
    "I've thought about that before — I'd probably want to see it work for someone I trust first.",
    "Depends on the price, if I'm being real with you. I'm not against trying new things, just cautious.",
    "Good question. I care more about it actually solving my problem than being flashy.",
]


def generate_mock_chat_reply(persona, history, message):
    """Generates a locally-fabricated in-character reply, no API call, no cost.
    Loosely reacts to the incoming message and pulls from this persona's own
    pain points so replies aren't identical across different personas."""
    pain_points = persona.get("painPoints") or ["something not working smoothly"]
    filler = random.choice(CHAT_FILLERS).replace(
        "my routine", f"my routine around {random.choice(pain_points).lower()}"
    )
    continuity = ""
    if len(history) >= 2:
        continuity = " Like I said earlier, that's still where I stand."
    return f"{filler}{continuity}"


def build_chat_system_prompt(persona, product_description, target_audience, research_objective):
    """System prompt that anchors the model in-character for the whole conversation."""
    traits = ", ".join(
        f"{t.get('trait')}: {t.get('score')}/100" for t in persona.get("personalityTraits", [])
    )
    behaviors = "; ".join(persona.get("behavioralPatterns", []))
    pain_points = "; ".join(persona.get("painPoints", []))
    return f"""You are role-playing as a synthetic research persona in an ongoing interview. Stay
strictly in character for every reply — never break character, never mention that you are
an AI or a simulation, and never refer to yourself as a "persona."

WHO YOU ARE:
Name: {persona.get('name')}
Age: {persona.get('age')}
Occupation: {persona.get('occupation')}
Location: {persona.get('location')}
Personality traits: {traits}
Behavioral patterns: {behaviors}
Psychological profile: {persona.get('psychProfile')}
Pain points: {pain_points}
Tech savviness: {persona.get('techSavviness')}

CONTEXT FOR THE INTERVIEW:
Product being discussed: {product_description}
Audience segment you belong to: {target_audience}
What the researcher is trying to learn: {research_objective}

Answer every question the way this specific person would — consistent with their traits
and profile above. Keep answers conversational, 1-4 sentences, first person. Maintain
consistency with anything you've said earlier in this conversation — don't contradict
yourself."""


@app.route("/api/interview-chat", methods=["POST"])
def interview_chat():
    body = request.get_json(silent=True) or {}

    persona = body.get("persona")
    product_description = body.get("productDescription")
    target_audience = body.get("targetAudience")
    research_objective = body.get("researchObjective")
    history = body.get("history", [])  # [{ role: "user" | "persona", content: "..." }]
    message = body.get("message")

    if not persona or not message:
        return jsonify({"error": "persona and message are required."}), 400

    if USE_MOCK:
        reply = generate_mock_chat_reply(persona, history, message)
        return jsonify({"reply": reply})

    try:
        system_prompt = build_chat_system_prompt(
            persona, product_description, target_audience, research_objective
        )

        # Translate our simple history format into Anthropic's messages format.
        anthropic_messages = []
        for turn in history:
            role = "assistant" if turn.get("role") == "persona" else "user"
            anthropic_messages.append({"role": role, "content": turn.get("content", "")})
        anthropic_messages.append({"role": "user", "content": message})

        response = client.messages.create(
            model=MODEL,
            max_tokens=500,
            system=system_prompt,
            messages=anthropic_messages,
        )

        reply_text = "\n".join(
            block.text for block in response.content if block.type == "text"
        ).strip()

        return jsonify({"reply": reply_text})

    except Exception as err:  # noqa: BLE001
        app.logger.exception("Error in interview chat")
        return jsonify({"error": str(err)}), 500


MOCK_THEMES = [
    {"theme": "Trust outweighs novelty", "description": "Most respondents wanted proof before switching, not just a compelling pitch.", "supportingCount": 0},
    {"theme": "Price sensitivity", "description": "Cost came up as a hesitation point even among otherwise interested respondents.", "supportingCount": 0},
    {"theme": "Peer validation matters", "description": "Recommendations from people they trust weighed more than advertising.", "supportingCount": 0},
]


def generate_mock_insights(personas, survey_results, interview_results):
    """Synthesizes fake-but-plausible insights locally from whatever data is present."""
    n_survey = len(survey_results.get("responses", [])) if survey_results else 0
    n_interview = len(interview_results.get("transcripts", [])) if interview_results else 0
    total_signals = max(n_survey + n_interview, 1)

    themes = []
    for i, t in enumerate(MOCK_THEMES):
        t = dict(t)
        t["supportingCount"] = max(1, round(total_signals * random.uniform(0.3, 0.8)))
        themes.append(t)

    positive = random.randint(30, 55)
    negative = random.randint(10, 30)
    neutral = max(0, 100 - positive - negative)

    agreement_patterns = [
        "Strong agreement that current habits are hard to break without a clear trigger.",
        "Split opinion on whether price or convenience matters more.",
    ]
    behavioral_trends = [
        "Respondents research before buying rather than acting on impulse.",
        "Word-of-mouth recommendations show up repeatedly as a deciding factor.",
    ]

    return {
        "themes": themes,
        "sentimentBreakdown": {"positive": positive, "neutral": neutral, "negative": negative},
        "agreementPatterns": agreement_patterns,
        "behavioralTrends": behavioral_trends,
        "summary": (
            f"Based on {n_survey} survey response(s) and {n_interview} interview "
            f"transcript(s), sentiment leans cautiously positive, with trust and price "
            f"as the recurring blockers."
        ),
        "dataCoverage": f"{n_survey} survey responses, {n_interview} interview transcripts analyzed",
    }


def build_insights_prompt(personas, survey_results, interview_results, product_description, research_objective):
    """Builds the instruction prompt for the Insight Extraction Agent."""
    survey_json = json.dumps(survey_results) if survey_results else "null"
    interview_json = json.dumps(interview_results) if interview_results else "null"
    return f"""You are an insight extraction agent for user research. Analyze the survey and
interview data below and surface recurring themes, sentiment, agreement patterns, and
behavioral trends.

PRODUCT: {product_description}
RESEARCH OBJECTIVE: {research_objective}

SURVEY SIMULATION RESULTS (may be null if not run):
{survey_json}

INTERVIEW SIMULATION RESULTS (may be null if not run):
{interview_json}

Return ONLY valid JSON (no markdown fences, no commentary) matching this exact schema:

{{
  "themes": [
    {{ "theme": "string", "description": "string", "supportingCount": number }}
  ],
  "sentimentBreakdown": {{ "positive": number, "neutral": number, "negative": number }},
  "agreementPatterns": ["string", "string"],
  "behavioralTrends": ["string", "string"],
  "summary": "string, 2-3 sentences",
  "dataCoverage": "string describing how much data was analyzed"
}}

sentimentBreakdown values should be percentages that sum to 100. If both survey and
interview data are null, base themes on the personas' profiles alone and note that in
dataCoverage."""


@app.route("/api/extract-insights", methods=["POST"])
def extract_insights():
    body = request.get_json(silent=True) or {}

    personas = body.get("personas", [])
    survey_results = body.get("surveyResults")
    interview_results = body.get("interviewResults")
    product_description = body.get("productDescription")
    research_objective = body.get("researchObjective")

    if not personas:
        return jsonify({"error": "personas is required — generate personas first."}), 400
    if not survey_results and not interview_results:
        return jsonify(
            {"error": "Run at least one of survey simulation or interview simulation first."}
        ), 400

    if USE_MOCK:
        return jsonify(generate_mock_insights(personas, survey_results, interview_results))

    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=3000,
            messages=[
                {
                    "role": "user",
                    "content": build_insights_prompt(
                        personas, survey_results, interview_results, product_description, research_objective
                    ),
                }
            ],
        )

        raw_text = "\n".join(
            block.text for block in message.content if block.type == "text"
        ).strip()

        cleaned = re.sub(r"^```json\s*|^```\s*|```$", "", raw_text, flags=re.MULTILINE).strip()

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            app.logger.error("Failed to parse model output as JSON: %s", cleaned)
            return jsonify({"error": "Model did not return valid JSON. Try again."}), 502

        return jsonify(parsed)

    except Exception as err:  # noqa: BLE001
        app.logger.exception("Error extracting insights")
        return jsonify({"error": str(err)}), 500


SEGMENT_REASONING_TEMPLATES = [
    "This group tends to weigh proven results heavily, which caps enthusiasm until they see it work for others.",
    "More willing to experiment, especially if the first step feels low-risk or free to try.",
    "Price and simplicity are the deciding factors more than features for this group.",
    "Trust in the brand matters more than the product's novelty for this segment.",
]


def generate_mock_adoption_score(personas, product_description):
    """Groups personas by tech savviness and fabricates a plausible adoption score per segment."""
    segments = {}
    for p in personas:
        seg = p.get("techSavviness", "Medium")
        segments.setdefault(seg, []).append(p)

    segment_results = []
    for seg, members in segments.items():
        score = random.randint(35, 85)
        segment_results.append(
            {
                "segment": f"{seg} tech savviness",
                "personaCount": len(members),
                "score": score,
                "reasoning": random.choice(SEGMENT_REASONING_TEMPLATES),
            }
        )

    overall = round(sum(s["score"] * s["personaCount"] for s in segment_results) / max(len(personas), 1))
    return {
        "overallScore": overall,
        "segments": segment_results,
        "summary": (
            f"Overall, simulated adoption interest for \"{product_description}\" sits around "
            f"{overall}/100, varying most by how experimental each segment is willing to be."
        ),
    }


def build_adoption_prompt(personas, product_description, target_audience, research_objective):
    """Builds the instruction prompt for adoption scoring, segmented by tech savviness."""
    persona_summaries = "\n".join(
        f"- {p.get('id')} | {p.get('name')} | Tech savviness: {p.get('techSavviness')} | "
        f"{p.get('psychProfile', '')}"
        for p in personas
    )
    return f"""You are scoring likely product adoption across synthetic persona segments.

PRODUCT: {product_description}
TARGET AUDIENCE: {target_audience}
RESEARCH OBJECTIVE: {research_objective}

PERSONAS (grouped conceptually by tech savviness — Low/Medium/High):
{persona_summaries}

Group the personas by their "Tech savviness" value into segments. For each segment,
estimate a 0-100 "would use this product" score grounded in the personas' profiles, and
give a one-sentence reasoning. Then compute an overall score weighted by segment size.

Return ONLY valid JSON (no markdown fences, no commentary) matching this exact schema:

{{
  "overallScore": number (0-100),
  "segments": [
    {{ "segment": "string e.g. 'High tech savviness'", "personaCount": number, "score": number (0-100), "reasoning": "string, one sentence" }}
  ],
  "summary": "string, 2-3 sentences"
}}"""


@app.route("/api/score-adoption", methods=["POST"])
def score_adoption():
    body = request.get_json(silent=True) or {}

    personas = body.get("personas", [])
    product_description = body.get("productDescription")
    target_audience = body.get("targetAudience")
    research_objective = body.get("researchObjective")

    if not personas:
        return jsonify({"error": "personas is required — generate personas first."}), 400

    if USE_MOCK:
        return jsonify(generate_mock_adoption_score(personas, product_description))

    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": build_adoption_prompt(
                        personas, product_description, target_audience, research_objective
                    ),
                }
            ],
        )

        raw_text = "\n".join(
            block.text for block in message.content if block.type == "text"
        ).strip()

        cleaned = re.sub(r"^```json\s*|^```\s*|```$", "", raw_text, flags=re.MULTILINE).strip()

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            app.logger.error("Failed to parse model output as JSON: %s", cleaned)
            return jsonify({"error": "Model did not return valid JSON. Try again."}), 502

        return jsonify(parsed)

    except Exception as err:  # noqa: BLE001
        app.logger.exception("Error scoring adoption")
        return jsonify({"error": str(err)}), 500


@app.route("/api/generate-personas", methods=["POST"])
def generate_personas():
    body = request.get_json(silent=True) or {}

    product_description = body.get("productDescription")
    target_audience = body.get("targetAudience")
    research_objective = body.get("researchObjective")
    count = body.get("count", 4)

    if not (product_description and target_audience and research_objective):
        return jsonify(
            {
                "error": "productDescription, targetAudience, and researchObjective are all required."
            }
        ), 400

    try:
        count = int(count)
    except (TypeError, ValueError):
        count = 4
    count = max(1, min(count, 100))

    if USE_MOCK:
        return jsonify(
            generate_mock_personas(
                product_description, target_audience, research_objective, count
            )
        )

    # Large batches are chunked into calls of at most 20 personas each — a single
    # call asking for e.g. 100 personas risks running past the response token
    # limit or the request timing out. Chunking keeps each call small and fast,
    # then the results are combined and re-numbered into one continuous list.
    CHUNK_SIZE = 20
    all_personas = []
    remaining = count
    try:
        while remaining > 0:
            chunk_count = min(CHUNK_SIZE, remaining)
            message = client.messages.create(
                model=MODEL,
                max_tokens=8000,
                messages=[
                    {
                        "role": "user",
                        "content": build_prompt(
                            product_description, target_audience, research_objective, chunk_count
                        ),
                    }
                ],
            )

            raw_text = "\n".join(
                block.text for block in message.content if block.type == "text"
            ).strip()

            cleaned = re.sub(r"^```json\s*|^```\s*|```$", "", raw_text, flags=re.MULTILINE).strip()

            try:
                parsed = json.loads(cleaned)
            except json.JSONDecodeError:
                app.logger.error("Failed to parse model output as JSON: %s", cleaned)
                return jsonify({"error": "Model did not return valid JSON. Try again."}), 502

            all_personas.extend(parsed.get("personas", []))
            remaining -= chunk_count

        # Re-number IDs sequentially across the combined batch.
        for i, p in enumerate(all_personas):
            p["id"] = f"P-{i + 1:04d}"

        return jsonify({"personas": all_personas})

    except Exception as err:  # noqa: BLE001
        app.logger.exception("Error generating personas")
        return jsonify({"error": str(err)}), 500


@app.route("/api/simulate-survey", methods=["POST"])
def simulate_survey():
    body = request.get_json(silent=True) or {}

    personas = body.get("personas")
    product_description = body.get("productDescription")
    target_audience = body.get("targetAudience")
    research_objective = body.get("researchObjective")
    questions = body.get("questions") or None

    if not personas:
        return jsonify({"error": "personas is required — generate personas first."}), 400
    if not (product_description and target_audience and research_objective):
        return jsonify(
            {
                "error": "productDescription, targetAudience, and researchObjective are all required."
            }
        ), 400

    if USE_MOCK:
        return jsonify(generate_mock_survey(personas, product_description, research_objective, questions))

    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=8000,
            messages=[
                {
                    "role": "user",
                    "content": build_survey_prompt(
                        personas, product_description, target_audience, research_objective, questions
                    ),
                }
            ],
        )

        raw_text = "\n".join(
            block.text for block in message.content if block.type == "text"
        ).strip()

        cleaned = re.sub(r"^```json\s*|^```\s*|```$", "", raw_text, flags=re.MULTILINE).strip()

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            app.logger.error("Failed to parse model output as JSON: %s", cleaned)
            return jsonify({"error": "Model did not return valid JSON. Try again."}), 502

        return jsonify(parsed)

    except Exception as err:  # noqa: BLE001
        app.logger.exception("Error simulating survey")
        return jsonify({"error": str(err)}), 500


@app.route("/api/simulate-interview", methods=["POST"])
def simulate_interview():
    body = request.get_json(silent=True) or {}

    personas = body.get("personas")
    product_description = body.get("productDescription")
    target_audience = body.get("targetAudience")
    research_objective = body.get("researchObjective")
    questions = body.get("questions") or DEFAULT_INTERVIEW_QUESTIONS

    if not personas:
        return jsonify({"error": "personas is required — generate personas first."}), 400
    if not (product_description and target_audience and research_objective):
        return jsonify(
            {
                "error": "productDescription, targetAudience, and researchObjective are all required."
            }
        ), 400

    if USE_MOCK:
        return jsonify(
            generate_mock_interview(personas, product_description, research_objective, questions)
        )

    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=8000,
            messages=[
                {
                    "role": "user",
                    "content": build_interview_prompt(
                        personas, product_description, target_audience, research_objective, questions
                    ),
                }
            ],
        )

        raw_text = "\n".join(
            block.text for block in message.content if block.type == "text"
        ).strip()

        cleaned = re.sub(r"^```json\s*|^```\s*|```$", "", raw_text, flags=re.MULTILINE).strip()

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            app.logger.error("Failed to parse model output as JSON: %s", cleaned)
            return jsonify({"error": "Model did not return valid JSON. Try again."}), 502

        return jsonify(parsed)

    except Exception as err:  # noqa: BLE001
        app.logger.exception("Error simulating interview")
        return jsonify({"error": str(err)}), 500


def build_research_report_pdf(data):
    """Compiles persona profiles, response highlights, insight summary, and
    validation scoring into a structured PDF using reportlab. Returns bytes."""
    from io import BytesIO
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    )

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        topMargin=0.75 * inch, bottomMargin=0.75 * inch,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleCustom", parent=styles["Title"], fontSize=20, spaceAfter=6)
    h2 = ParagraphStyle("H2Custom", parent=styles["Heading2"], spaceBefore=16, spaceAfter=8)
    h3 = ParagraphStyle("H3Custom", parent=styles["Heading3"], spaceBefore=10, spaceAfter=4)
    body = styles["BodyText"]
    small = ParagraphStyle("Small", parent=styles["BodyText"], fontSize=9, textColor=colors.grey)

    story = []
    story.append(Paragraph("Synthetic User Research — Report", title_style))
    story.append(Paragraph(f"Product: {data.get('productDescription', '—')}", body))
    story.append(Paragraph(f"Target audience: {data.get('targetAudience', '—')}", body))
    story.append(Paragraph(f"Research objective: {data.get('researchObjective', '—')}", body))
    story.append(Spacer(1, 12))

    personas = data.get("personas", [])
    story.append(Paragraph(f"Persona Profiles ({len(personas)})", h2))
    for p in personas:
        story.append(Paragraph(f"{p.get('name')} — {p.get('age')}, {p.get('occupation')}", h3))
        story.append(Paragraph(f"\u201c{p.get('quote', '')}\u201d", small))
        story.append(Paragraph(p.get("psychProfile", ""), body))
        story.append(Spacer(1, 6))

    survey = data.get("surveyResults")
    if survey:
        story.append(PageBreak())
        story.append(Paragraph("Survey Simulation — Response Highlights", h2))
        counts = survey.get("summary", {}).get("counts", {})
        table_data = [["Stance", "Count"]] + [[k, str(v)] for k, v in counts.items()]
        t = Table(table_data, colWidths=[3 * inch, 1.5 * inch])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2F6D63")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
        ]))
        story.append(t)
        story.append(Spacer(1, 8))
        story.append(Paragraph(survey.get("summary", {}).get("keyInsight", ""), body))
        story.append(Spacer(1, 10))
        for r in survey.get("responses", [])[:10]:
            story.append(Paragraph(f"{r.get('name')} — {r.get('stance')} ({r.get('confidence')}%)", small))
            story.append(Paragraph(f"\u201c{r.get('quote', '')}\u201d", body))

    interview = data.get("interviewResults")
    if interview:
        story.append(PageBreak())
        story.append(Paragraph("Interview Simulation — Response Highlights", h2))
        for theme in interview.get("themes", []):
            story.append(Paragraph(f"• {theme}", body))
        story.append(Spacer(1, 8))
        for t in interview.get("transcripts", [])[:10]:
            story.append(Paragraph(f"{t.get('name')}", h3))
            for qa in t.get("qa", [])[:2]:
                story.append(Paragraph(f"Q: {qa.get('question')}", small))
                story.append(Paragraph(f"A: {qa.get('answer')}", body))
            story.append(Spacer(1, 6))

    insights = data.get("insights")
    if insights:
        story.append(PageBreak())
        story.append(Paragraph("Insight Summary", h2))
        story.append(Paragraph(insights.get("summary", ""), body))
        sentiment = insights.get("sentimentBreakdown", {})
        if sentiment:
            story.append(Paragraph(
                f"Sentiment — Positive: {sentiment.get('positive', 0)}%, "
                f"Neutral: {sentiment.get('neutral', 0)}%, "
                f"Negative: {sentiment.get('negative', 0)}%", body
            ))
        story.append(Spacer(1, 8))
        for theme in insights.get("themes", []):
            story.append(Paragraph(f"{theme.get('theme')} ({theme.get('supportingCount')} signals)", h3))
            story.append(Paragraph(theme.get("description", ""), body))

    adoption = data.get("adoptionResult")
    if adoption:
        story.append(PageBreak())
        story.append(Paragraph("Validation Scoring — Would People Use This?", h2))
        story.append(Paragraph(f"Overall score: {adoption.get('overallScore')}/100", h3))
        story.append(Paragraph(adoption.get("summary", ""), body))
        story.append(Spacer(1, 8))
        seg_data = [["Segment", "Score", "People", "Reasoning"]]
        for s in adoption.get("segments", []):
            seg_data.append([s.get("segment"), str(s.get("score")), str(s.get("personaCount")), s.get("reasoning", "")[:60]])
        t = Table(seg_data, colWidths=[1.3 * inch, 0.6 * inch, 0.6 * inch, 3 * inch])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#C8963A")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(t)

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


@app.route("/api/generate-report", methods=["POST"])
def generate_report():
    body = request.get_json(silent=True) or {}

    if not body.get("personas"):
        return jsonify({"error": "personas is required — generate personas first."}), 400

    try:
        pdf_bytes = build_research_report_pdf(body)
    except ImportError:
        return jsonify(
            {"error": "reportlab is not installed. Run: pip install reportlab"}
        ), 500
    except Exception as err:  # noqa: BLE001
        app.logger.exception("Error generating report")
        return jsonify({"error": str(err)}), 500

    from flask import Response
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment; filename=research-report.pdf"},
    )


@app.route("/api/health")
def health():
    return jsonify({"ok": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3001))
    app.run(host="0.0.0.0", port=port, debug=True)
