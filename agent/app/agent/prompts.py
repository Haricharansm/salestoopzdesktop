import json

def prompt_positioning(offering: dict, icp: dict) -> str:
    return f"""
SYSTEM:
You are an expert B2B outbound strategist. Return ONLY valid JSON. No markdown.

USER:
Create positioning for outbound email outreach.

OFFERING:
{json.dumps(offering)}

ICP:
{json.dumps(icp)}

CONSTRAINTS:
- No hype, no unverifiable claims
- Keep it practical and concise

Return ONLY JSON:
{{
  "target_customer": "",
  "pain_points": [],
  "value_prop": "",
  "differentiators": [],
  "proof_points": [],
  "objections": [{{"objection":"", "rebuttal":""}}],
  "tone": {{"voice":"", "reading_level":"", "no_go":[]}}
}}
""".strip()


def prompt_messaging(offering: dict, icp: dict, positioning: dict) -> str:
    return f"""
SYSTEM:
You are a B2B cold email copywriter. Return ONLY valid JSON. No markdown.

USER:
Generate messaging assets using the positioning.

OFFERING:
{json.dumps(offering)}

ICP:
{json.dumps(icp)}

POSITIONING:
{json.dumps(positioning)}

Return ONLY JSON:
{{
  "themes": [{{"name":"", "why_it_works":"", "talk_tracks":[]}}],
  "subject_lines": [],
  "openers": [],
  "cta_options": [],
  "personalization_slots": [{{"slot":"", "how_to_fill":""}}]
}}
""".strip()


def prompt_sequence(offering: dict, icp: dict, positioning: dict, messaging: dict) -> str:
    return f"""
SYSTEM:
You design outbound sequences. Return ONLY valid JSON. No markdown.

USER:
Design an EMAIL-ONLY outreach sequence.

RULES:
- 4 to 6 steps total
- each email < 120 words
- include a soft "right person?" CTA at least once
- include opt-out line in final step

OFFERING:
{json.dumps(offering)}

ICP:
{json.dumps(icp)}

POSITIONING:
{json.dumps(positioning)}

MESSAGING:
{json.dumps(messaging)}

Return ONLY JSON:
{{
  "sequence_name": "",
  "primary_channel": "email",
  "steps": [
    {{
      "step_id": "E1",
      "channel": "email",
      "delay_hours_from_prev": 0,
      "goal": "",
      "template": {{ "subject": "", "body": "" }}
    }}
  ],
  "stop_rules": {{ "stop_on_reply": true, "stop_on_oOO": true, "stop_on_bounce": true }}
}}
""".strip()

