
from typing import Any, Dict
from pathlib import Path
import json, re, importlib, os
from pydantic import BaseModel, Field
from rich.console import Console

console = Console()
TEMPL_RE = re.compile(r"\{\{([^}]+)\}\}")

class StepModel(BaseModel):
    id: str
    agent: str
    inputs: Dict[str, Any] = Field(default_factory=dict)
    instructions: str = None

class WorkflowModel(BaseModel):
    workflow_name: str
    mode: str = "mock"
    description: str = None
    steps: list[StepModel]

def load_workflow(path: str = "workflow.json") -> WorkflowModel:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"workflow.json not found at {p.resolve()}")
    raw = json.loads(p.read_text())
    return WorkflowModel(**raw)

def resolve_template_string(s: str, context: Dict[str, Any]):
    def repl(m):
        ref = m.group(1).strip()
        parts = ref.split('.')
        cur = context
        try:
            for p in parts:
                if isinstance(cur, list) and p.isdigit():
                    cur = cur[int(p)]
                else:
                    cur = cur[p]
            return json.dumps(cur) if isinstance(cur, (dict, list)) else str(cur)
        except Exception:
            return m.group(0)
    return TEMPL_RE.sub(repl, s)

def deep_resolve(obj, context):
    if isinstance(obj, str):
        return resolve_template_string(obj, context)
    if isinstance(obj, dict):
        return {k: deep_resolve(v, context) for k, v in obj.items()}
    if isinstance(obj, list):
        return [deep_resolve(v, context) for v in obj]
    return obj

def camel_to_snake(name: str) -> str:
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    return s2.replace('__','_').lower()

def instantiate_agent(agent_name: str, config: Dict[str, Any]):
    module_slug = camel_to_snake(agent_name).replace('_agent','')
    module_path = f"agents.{module_slug}"
    mod = importlib.import_module(module_path)
    cls = getattr(mod, agent_name)
    return cls(config)

def run_workflow(workflow: WorkflowModel, save_output: bool = True) -> Dict[str, Any]:
    mode = workflow.mode or os.getenv("WORKFLOW_MODE","mock")
    console.print(f"[bold]Workflow:[/bold] {workflow.workflow_name}  [bold]Mode:[/bold] {mode}\n")
    context = {"config": workflow.model_dump()}
    outputs = {}
    for step in workflow.steps:
        sid = step.id
        agent_name = step.agent
        console.rule(f"[blue]Step: {sid} -> {agent_name}")
        raw_inputs = step.inputs or {}
        resolved_inputs = deep_resolve(raw_inputs, {**context, **outputs})
        # parse JSON strings
        def try_parse(v):
            if isinstance(v, str):
                try:
                    return json.loads(v)
                except Exception:
                    return v
            return v
        if isinstance(resolved_inputs, dict):
            resolved_inputs = {k: try_parse(v) for k, v in resolved_inputs.items()}
        console.print(f"[yellow]Resolved inputs for {sid}:[/yellow]")
        console.print_json(json.dumps(resolved_inputs, default=str))
        try:
            agent = instantiate_agent(agent_name, step.model_dump())
        except Exception as e:
            console.print(f"[red]Agent import failed for {agent_name}: {e}[/red]")
            outputs[sid] = {"output": {"error": f"import_error: {e}"}}
            continue
        try:
            out = agent.run(resolved_inputs)
            outputs[sid] = {"output": out}
            console.print(f"[green]Output from {sid}:[/green]")
            console.print_json(json.dumps(out, default=str))
        except Exception as e:
            # Log the error for this step and continue the next steps
            console.print(f"[red]Step {sid} failed: {e}[/red]")
            outputs[sid] = {"output": {"error": str(e)}}
            continue

    if save_output:
        Path("demo_output.json").write_text(json.dumps(outputs, indent=2, default=str))
        console.print(f"[bold]Saved outputs to demo_output.json[/bold]")
    return outputs

def main():
    wf = load_workflow()
    run_workflow(wf)

if __name__ == "__main__":
    main()
