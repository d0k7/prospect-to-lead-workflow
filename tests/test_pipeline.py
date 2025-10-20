import json
from pathlib import Path
from langgraph_builder import load_workflow, run_workflow

def test_workflow_load_and_run():
    wf = load_workflow("workflow.json")
    outputs = run_workflow(wf, save_output=False)
    assert isinstance(outputs, dict)
    # ensure expected step keys exist
    assert "prospect_search" in outputs
    assert "enrichment" in outputs
