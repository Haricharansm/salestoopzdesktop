from datetime import datetime, timezone
from typing import Dict, Any

from app.llm.ollama_client import generate_json
from app.agent.prompts import positioning_prompt, messaging_prompt, sequence_prompt


class StrategyAgent:
    """
    Strategy Agent = THINKING ONLY.
    Outputs strategy_json + runner-ready sequence_json + run_config_json.
    """

    async def generate_positioning(self, offering: Dict[str, Any], icp: Dict[str, Any]) -> Dict[str, Any]:
        prompt = positioning_prompt(offering, icp)
        return generate_json(prompt, temperature=0.3)

    async def generate_messaging(self, offering: Dict[str, Any], icp: Dict[str, Any], positioning: Dict[str, Any]) -> Dict[str, Any]:
        prompt = messaging_prompt(offering, icp, positioning)
        return generate_json(prompt, temperature=0.35)

    async def generate_sequence(
        self,
        offering: Dict[str, Any],
        icp: Dict[str, Any],
        positioning: Dict[str, Any],
        messaging: Dict[str, Any],
    ) -> Dict[str, Any]:
        prompt = sequence_prompt(offering, icp, positioning, messaging)
        return generate_json(prompt, temperature=0.35)

    def compose_campaign_strategy(
        self,
        offering: Dict[str, Any],
        icp: Dict[str, Any],
        positioning: Dict[str, Any],
        messaging: Dict[str, Any],
        sequence_plan: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "schema_version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "inputs": {"offering": offering, "icp": icp},
            "positioning": positioning,
            "messaging": messaging,
            "sequence_plan": sequence_plan,
            "guardrails": {
                "compliance": ["no false claims", "honor opt-out immediately"]
            },
            "notes": {
                "assumptions": [],
                "recommended_enrichment": []
            }
        }

    def to_runner_sequence_json(self, sequence_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converts strategy output into runner-friendly operational format.
        """
        steps = []
        templates = {}

        for step in sequence_plan.get("steps", []):
            sid = step["step_id"]
            templates[sid] = step["template"]
            steps.append({
                "step_id": sid,
                "type": "send_email",
                "channel": step.get("channel", "email"),
                "delay_hours": int(step.get("delay_hours_from_prev", 0)),
                "template_key": sid,
                "variants": ["v1"],
                "stop_if": ["replied", "bounced", "unsubscribed"]
            })

        return {
            "schema_version": "1.0",
            "steps": steps,
            "templates": templates
        }

    def default_run_config(self) -> Dict[str, Any]:
        return {
            "schema_version": "1.0",
            "timezone": "America/Chicago",
            "quiet_hours": {"start": "20:00", "end": "08:00"},
            "daily_send_limit": 50,
            "max_concurrent_leads": 10,
            "min_minutes_between_sends": 2,
            "allowed_days": ["Mon", "Tue", "Wed", "Thu", "Fri"]
        }
