"""Data enrichment (mock)"""

from .base_agent import BaseAgent
from typing import Dict, Any, List
import random

class DataEnrichmentAgent(BaseAgent):
    """Mock enrichment: add domain, title, tech_stack."""

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        leads = inputs.get("leads", [])
        enriched: List[Dict[str, Any]] = []
        for lead in leads:
            domain = lead.get("company", "").replace(" ", "").lower() + ".com"
            lead_enriched = {**lead,
                             "domain": domain,
                             "title": random.choice(["CEO", "Head of GTM", "VP Sales"]),
                             "tech_stack": random.sample(["aws", "gcp", "stripe", "segment", "postgres"], 2)}
            enriched.append(lead_enriched)
        return {"enriched_leads": enriched}
