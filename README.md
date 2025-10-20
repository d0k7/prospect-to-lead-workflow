# prospect-to-lead-workflow

prospect-to-lead-workflow/
│
├── README.md
├── workflow.json
├── langgraph_builder.py
├── requirements.txt
├── demo_output.json
│
├── agents/
│   ├── __init__.py
│   ├── base_agent.py
│   ├── prospect_search.py
│   ├── data_enrichment.py
│   ├── scoring.py
│   ├── outreach_content.py
│   ├── outreach_executor.py
│   ├── response_tracker.py
│   └── feedback_trainer.py
│
└── tests/
    └── test_pipeline.py

# Prospect-to-Lead Workflow (LangGraph-based)

This repository contains my implementation of the **Prospect-to-Lead Workflow** assignment, built with modular agents, a workflow orchestrator (`langgraph_builder.py`), and optional OpenAI-powered outreach content generation.

---

## 🚀 Overview

The project demonstrates an automated **prospecting-to-outreach** pipeline that connects multiple agents in sequence:
1. **ProspectSearchAgent** — finds potential leads.
2. **DataEnrichmentAgent** — enriches lead data with mock details.
3. **ScoringAgent** — scores and ranks leads.
4. **OutreachContentAgent** — generates outreach messages (OpenAI live-capable).
5. **OutreachExecutorAgent** — simulates email sending.
6. **ResponseTrackerAgent** — mocks engagement tracking.
7. **FeedbackTrainerAgent** — generates campaign feedback and improvement suggestions.

All agents communicate via JSON and are orchestrated through a workflow defined in `workflow.json`.

---

## 🧩 Features

- ✅ Modular agent-based architecture  
- ✅ End-to-end workflow execution  
- ✅ OpenAI integration (with graceful fallback when quota/rate-limited)  
- ✅ Safe mock mode for reproducible runs  
- ✅ Structured JSON I/O (`demo_output.json`)  
- ✅ Logging and error resilience per step  
- ✅ Ready for future API integrations (Clay, Apollo, Clearbit, SendGrid, Google Sheets)

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **LangGraph-style orchestration**
- **Pydantic v2**
- **OpenAI API (optional, for OutreachContentAgent)**
- **pytest** for testing

---

## 📦 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/dheerajmishra/prospect-to-lead-workflow.git
   cd prospect-to-lead-workflow

## Install dependencies
pip install -r requirements.txt


## Set environment variables
export OPENAI_API_KEY="your_api_key_here"
export WORKFLOW_MODE="live"

## (Or use WORKFLOW_MODE=mock for fully offline runs)


## Running the Workflow

python3 langgraph_builder.py


## Testing

pytest -q



