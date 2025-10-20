
"""OutreachContentAgent with exponential backoff + jitter."""

from typing import Dict, Any, List
import os, time, json, re, random, logging
from agents.base_agent import BaseAgent

logger = logging.getLogger("langgraph")

try:
    from openai import OpenAI
    try:
        from openai.error import RateLimitError
    except Exception:
        RateLimitError = Exception
except Exception:
    OpenAI = None
    RateLimitError = Exception

class OutreachContentAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        if OpenAI is not None and self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"OpenAI client init failed: {e}; will fallback.")
                self.client = None
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "120"))
        self.batch_sleep = float(os.getenv("OUTREACH_BATCH_SLEEP", "0.6"))
        self.max_attempts = int(os.getenv("OUTREACH_MAX_ATTEMPTS", "3"))
        self.base_backoff = float(os.getenv("OUTREACH_BASE_BACKOFF", "1.0"))

    def _build_prompt(self, lead: Dict[str, Any], persona: str, tone: str) -> str:
        return (
            f"You are an outbound SDR writing a short cold email (subject + one short paragraph body) "
            f"for the {persona} persona. Tone: {tone}.\\n\\n"
            f"Lead company: {lead.get('company')}\\n"
            f"Contact name: {lead.get('contact_name')}\\n"
            f"Relevant signals: {lead.get('signal')}\\n"
            f"Tech stack: {', '.join(lead.get('tech_stack', []))}\\n\\n"
            "Requirements:\\n- Subject: 3-6 words emphasizing outcome.\\n"
            "- Body: <= 80 words, short social proof clause, single CTA.\\n"
            "- Output JSON ONLY with keys: subject, body.\\n\\n"
            "Now produce the JSON only."
        )

    def _extract_json(self, raw: str) -> Dict[str, str]:
        try:
            return json.loads(raw)
        except Exception:
            m = re.search(r"(\\{.*\\})", raw, flags=re.S)
            if m:
                try:
                    return json.loads(m.group(1))
                except Exception:
                    pass
        return {}

    def _call_with_backoff(self, prompt: str) -> str:
        if self.client is None:
            raise RuntimeError("OpenAI client not configured.")
        last_exc = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role":"system","content":"You are a helpful assistant that outputs JSON."},
                              {"role":"user","content":prompt}],
                    max_tokens=self.max_tokens,
                    temperature=0.2,
                    timeout=30
                )
                if hasattr(resp, "choices") and len(resp.choices) > 0:
                    choice = resp.choices[0]
                    if hasattr(choice, "message") and getattr(choice.message, "content", None):
                        return choice.message.content
                    if getattr(choice, "text", None):
                        return choice.text
                if getattr(resp, "output_text", None):
                    return resp.output_text
                if getattr(resp, "text", None):
                    return resp.text
                return str(resp)
            except Exception as e:
                last_exc = e
                # if fatal quota error, stop retrying
                if isinstance(e, RateLimitError) or getattr(e, "http_status", None) == 429 or getattr(e, "code", None) == "insufficient_quota":
                    logger.error(f"Fatal OpenAI rate/quota error: {e}")
                    break
                backoff = self.base_backoff * (2 ** (attempt - 1))
                jitter = random.uniform(0, backoff * 0.5)
                wait = backoff + jitter
                logger.warning(f"OpenAI call failed attempt {attempt}: {e}. Backing off {wait:.2f}s.")
                time.sleep(wait)
        raise last_exc

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        ranked = inputs.get("ranked_leads", [])
        persona = inputs.get("persona", "SDR")
        tone = inputs.get("tone", "friendly")
        messages: List[Dict[str, str]] = []
        for lead in ranked:
            if not self.client:
                # deterministic fallback
                subject = f"Quick question about {lead.get('company')}"
                body = (f"Hi {lead.get('contact_name')},\\n\\n"
                        f"I noticed {lead.get('company')} is {lead.get('signal')} and using {', '.join(lead.get('tech_stack', []))}. "
                        "Would you be open to a quick 15-min chat?\\n\\nBest,\\n" + persona)
            else:
                prompt = self._build_prompt(lead, persona, tone)
                try:
                    raw = self._call_with_backoff(prompt)
                    parsed = self._extract_json(raw)
                    subject = parsed.get("subject") or f"Quick question about {lead.get('company')}"
                    body = parsed.get("body") or (f"Hi {lead.get('contact_name')},\\n\\nQuick note: would you be open to a 15-min chat?\\n\\nBest,\\n{persona}")
                except Exception as e:
                    logger.error(f"OpenAI generation failed for {lead.get('company')}: {e}")
                    subject = f"Quick question about {lead.get('company')}"
                    body = (f"Hi {lead.get('contact_name')},\\n\\n"
                            f"I noticed {lead.get('company')} is {lead.get('signal')} and using {', '.join(lead.get('tech_stack', []))}. "
                            "Would you be open to a quick 15-min chat?\\n\\nBest,\\n" + persona)
            messages.append({"lead_company": lead.get("company"), "email_subject": subject.strip(), "email_body": body.strip()})
            time.sleep(self.batch_sleep)
        return {"messages": messages}
