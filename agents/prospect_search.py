"""Prospect search (mock)"""

from .base_agent import BaseAgent
from typing import Dict, Any, List
import random

class ProspectSearchAgent(BaseAgent):
    """Mock prospect search; in production replace with Clay/Apollo calls."""

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        icp = inputs.get("icp", {})
        signals = inputs.get("signals", ["recent_funding"])
        companies = ["Acme SaaS", "Nimbus Analytics", "PulseSoft", "BrightLayer"]
        leads: List[Dict[str, Any]] = []
        for i, comp in enumerate(companies):
            leads.append({
                "company": comp,
                "contact_name": f"{comp.split()[0]} Founder",
                "email": f"founder@{comp.replace(' ','').lower()}.com",
                "linkedin": f"https://linkedin.com/in/{comp.replace(' ','').lower()}",
                "signal": random.choice(signals)
            })
        return {"leads": leads}
