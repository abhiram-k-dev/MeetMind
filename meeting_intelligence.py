from dotenv import load_dotenv
load_dotenv()

import os
import json
from google import genai

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

SYSTEM_PROMPT = """You are MeetMind, an enterprise meeting intelligence agent.
You are given:
1. A raw meeting transcript.
2. A "Work IQ context package" containing the employee directory,
   related prior emails, and related prior meetings.

Your job is to produce a structured JSON output with exactly these keys:

1. "decision_log": an object with three keys "context", "resolution",
   "forward_trajectory" — each value must be EXACTLY ONE sentence.
   - context: why the meeting happened / the core topic or conflict.
   - resolution: the definitive decision reached.
   - forward_trajectory: the immediate next milestone and its impact.

2. "action_items": a list of objects, each with:
   - "assignee_name": the person's real name
   - "assignee_email": resolved from the employee directory if possible
   - "task": a clear, specific description of the task
   - "due_context": any deadline mentioned (or "Not specified")
   - "linked_context": if this task relates to a prior email or meeting
     in the Work IQ context package, briefly note which one and why.
     Otherwise "None".

3. "follow_up_emails": a list of objects, each with:
   - "to_name": recipient's real name
   - "to_email": resolved from employee directory if possible
   - "subject": a concise subject line
   - "body": a professional email body referencing the decision log
     and that person's specific action items. Sign off as "Rahul"
     (the meeting organizer) unless transcript indicates otherwise.

Use the Work IQ context to disambiguate names, resolve references like
"Vishnu's strategy" to the correct prior proposal, and link action items
to prior context where relevant. Resolve any pronoun/self-reference
confusion in the transcript using context clues.

Respond with ONLY the JSON object. No markdown fences, no preamble.
"""


def generate(transcript: str, context_package: dict) -> dict:
    user_message = f"""MEETING TRANSCRIPT:
{transcript}

WORK IQ CONTEXT PACKAGE:
{json.dumps(context_package, indent=2)}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_message,
        config={
            "system_instruction": SYSTEM_PROMPT,
            "response_mime_type": "application/json",
        },
    )

    raw_text = response.text.strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        return {"error": "Failed to parse model output", "raw": raw_text}


def extract_topic_keywords(transcript: str) -> list:
    """
    Simple keyword extraction to query Work IQ. For the hackathon MVP
    this is a lightweight heuristic; in production this could itself
    be an LLM call or use Work IQ's own topic extraction.
    """
    common_words = {"the", "and", "for", "with", "this", "that", "from",
                     "have", "will", "okay", "right", "just", "sure"}
    words = [w.strip(".,!?'\"").lower() for w in transcript.split()]
    keywords = [w for w in words if len(w) > 4 and w not in common_words]
    seen = []
    for w in keywords:
        if w not in seen:
            seen.append(w)
    return seen[:8]