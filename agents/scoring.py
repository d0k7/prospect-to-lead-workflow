"""Scoring agent (mock)"""

from .base_agent import BaseAgent
from typing import Dict, Any, List

class ScoringAgent(BaseAgent):
    """Simple rule-based scoring for demo."""

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        leads = inputs.get("leads", [])
        ranked: List[Dict[str, Any]] = []
        for lead in leads:
            score = 0
            if lead.get("signal") == "recent_funding":
                score += 40
            tech_stack = lead.get("tech_stack", [])
            score += min(20, 5 * len(tech_stack))
            if len(lead.get("company", "")) < 20:
                score += 10
            lead["score"] = score
            ranked.append(lead)
        ranked.sort(key=lambda x: x["score"], reverse=True)
        return {"ranked_leads": ranked}
