"""Response tracker (mock): generate simple metrics."""

from .base_agent import BaseAgent
from typing import Dict, Any
import random

class ResponseTrackerAgent(BaseAgent):
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        sent = inputs.get("sent", [])
        opens = random.randint(10, 50)
        clicks = random.randint(0, 10)
        replies = random.randint(0, 5)
        return {"metrics": {"opens": opens, "clicks": clicks, "replies": replies}}
