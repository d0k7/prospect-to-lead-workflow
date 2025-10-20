"""Outreach executor (mock): pretend to send emails / queue them."""

from .base_agent import BaseAgent
from typing import Dict, Any, List
import time

class OutreachExecutorAgent(BaseAgent):
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        messages = inputs.get("messages", [])
        sent: List[Dict[str, Any]] = []
        for msg in messages:
            # simulate send latency
            time.sleep(0.02)
            sent.append({"to_company": msg["lead_company"], "status": "queued", "subject": msg["email_subject"]})
        return {"sent": sent}
