from typing import Any, Dict, List, TypedDict


class Positioning(TypedDict):
    target_customer: str
    pain_points: List[str]
    value_prop: str
    differentiators: List[str]
    proof_points: List[str]
    objections: List[Dict[str, str]]
    tone: Dict[str, Any]


class Messaging(TypedDict):
    themes: List[Dict[str, Any]]
    subject_lines: List[str]
    openers: List[str]
    cta_options: List[str]
    personalization_slots: List[Dict[str, str]]


class SequenceStep(TypedDict):
    step_id: str
    channel: str
    delay_hours_from_prev: int
    goal: str
    template: Dict[str, str]


class SequencePlan(TypedDict):
    sequence_name: str
    primary_channel: str
    steps: List[SequenceStep]
    stop_rules: Dict[str, bool]
