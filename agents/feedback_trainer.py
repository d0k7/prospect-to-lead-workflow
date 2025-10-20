"""Feedback trainer (mock): produce recommendations from metrics."""

from .base_agent import BaseAgent
from typing import Dict, Any, List

class FeedbackTrainerAgent(BaseAgent):
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        metrics = inputs.get("metrics", {})
        messages = inputs.get("messages", [])
        recs: List[str] = []
        opens = metrics.get("opens", 0)
        replies = metrics.get("replies", 0)
        if opens < 20:
            recs.append("Subject lines are weak — test 3 new variants focused on outcomes.")
        if replies < 2:
            recs.append("Messages may be too generic — add specific case study + CTA variation.")
        if not recs:
            recs.append("Performance looks good — continue current cadence.")
        # In prod: write to Google Sheets or trigger human approval flow.
        return {"recommendations": recs}
