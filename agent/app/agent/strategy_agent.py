from app.llm.ollama_client import generate_json
from app.agent.prompts import prompt_positioning, prompt_messaging, prompt_sequence

class StrategyAgent:
    """
    THINKING only. Outputs strategy + runner-ready sequence + run config.
    """

    async def generate_positioning(self, offering: dict, icp: dict) -> dict:
        return generate_json(prompt_positioning(offering, icp))

    async def generate_messaging(self, offering: dict, icp: dict, positioning: dict) -> dict:
        return generate_json(prompt_messaging(offering, icp, positioning))

    async def generate_sequence(self, offering: dict, icp: dict, positioning: dict, messaging: dict) -> dict:
        return generate_json(prompt_sequence(offering, icp, positioning, messaging))

    def compose_campaign_strategy(self, offering, icp, positioning, messaging, sequence_plan) -> dict:
        return {
            "schema_version": "1.0",
            "inputs": {"offering": offering, "icp": icp},
            "positioning": positioning,
            "messaging": messaging,
            "sequence_plan": sequence_plan,
            "guardrails": {
                "compliance": ["no false claims", "honor opt-out immediately"]
            }
        }

    def to_runner_sequence_json(self, sequence_plan: dict) -> dict:
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
                "stop_if": ["replied", "bounced", "unsubscribed"]
            })

        return {"schema_version": "1.0", "steps": steps, "templates": templates}

    def default_run_config(self) -> dict:
        return {
            "schema_version": "1.0",
            "timezone": "America/Chicago",
            "quiet_hours": {"start": "20:00", "end": "08:00"},
            "daily_send_limit": 50,
            "max_concurrent_leads": 10,
            "min_minutes_between_sends": 2,
            "allowed_days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
        }

