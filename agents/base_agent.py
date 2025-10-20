"""Base Agent abstraction for the LangGraph pipeline."""

from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

logger = logging.getLogger("langgraph")
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

class BaseAgent(ABC):
    """Abstract base class for all agents.

    Each agent receives a config (the step dict from workflow.json) and inputs (resolved).
    The agent returns a structured JSON-serializable dict as output.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.step_id = config.get("id", "unknown")

    @abstractmethod
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Run agent logic and return a dict."""
        raise NotImplementedError
