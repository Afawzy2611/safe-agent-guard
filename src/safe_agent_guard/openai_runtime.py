from __future__ import annotations

import os
from typing import Dict, List

from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from src.safe_agent_guard.models import Action
from src.safe_agent_guard.policy import evaluate_action
from src.safe_agent_guard.openai_runtime import OpenAIAgentRuntime

app = FastAPI(title=os.getenv("APP_TITLE", "Safe Agent Guard"))
agent_runtime = OpenAIAgentRuntime(api_key=os.getenv("OPENAI_API_KEY"))

class TaskCreateRequest(BaseModel):
    task: str
    requested_kind: str | None = None

class TaskDecisionRequest(BaseModel):
    approved: bool

TASKS: Dict[str, Dict[str, object]] = {}


def render_form() -> str:
    return """
    <html>
      <head>
        <title>Safe Agent Guard</title>
        <style>
          body { font-family: sans-serif; margin: 40px; background: #0b1020; color: #e5e7eb; }
          form { max-width: 700px; background: #111827; padding: 24px; border-radius: 12px; }
          input, select, button { width: 100%; margin-bottom: 12px; padding: 10px; border-radius: 8px; border: 1px solid #374151; }
          button { background: #2563eb; color: white; border: none; cursor: pointer; }
          .task { margin-top: 18px; padding: 18px; background: #0f172a; border-radius: 12px; }
          pre { white-space: pre-wrap; word-break: break-word; }
        </style>
      </head>
      <body>
        <h1>Safe Agent Guard</h1>
        <form action="/api/tasks" method="post">
          <label for="task">Task</label>
          <input id="task" name="task" placeholder="Example: deploy the latest release to production" required />
          <label for="requested_kind">Requested kind</label>
          <select id="requested_kind" name="requested_kind">
            <option value="search">search</option>
            <option value="edit">edit</option>
            <option value="test">test</option>
            <option value="deploy">deploy</option>
          </select>
          <button type="submit">Create task</button>
        </form>
      </body>
    </html>
    """


@app.get("/", response_class=HTMLResponse)
async def index():
    return render_form()


@app.post("/api/tasks")
async def create_task(task: str = Form(...), requested_kind: str = Form("search")):
    action = agent_runtime.plan_action(task, requested_kind)
    decision = evaluate_action(action)

    task_id = str(len(TASKS) + 1)
    TASKS[task_id] = {
        "task": task,
        "action": action,
        "decision": decision,
        "approved": False,
        "status": "pending" if decision.requires_approval else "ready",
    }

    return {
        "task_id": task_id,
        "task": task,
        "action": {
            "name": action.name,
            "kind": action.kind,
            "path": action.path,
            "command": action.command,
            "description": action.description,
        },
        "decision": {
            "allowed": decision.allowed,
            "requires_approval": decision.requires_approval,
            "requires_sandbox": decision.requires_sandbox,
            "requires_rollback": decision.requires_rollback,
            "reason": decision.reason,
            "risk_level": decision.risk_level.value if decision.risk_level else None,
        },
        "status": TASKS[task_id]["status"],
    }


@app.post("/api/tasks/{task_id}/approve")
async def approve_task(task_id: str, approved: bool = Form(False)):
    if task_id not in TASKS:
        raise HTTPException(status_code=404, detail="Task not found")

    task_record = TASKS[task_id]
    task_record["approved"] = approved
    task_record["status"] = "approved" if approved else "rejected"

    return {
        "task_id": task_id,
        "status": task_record["status"],
        "approved": approved,
        "action": task_record["action"].name,
    }


@app.get("/api/tasks")
async def list_tasks():
    return {"tasks": [{
        "task_id": task_id,
        "status": record["status"],
        "task": record["task"],
        "action": record["action"].name,
    } for task_id, record in TASKS.items()]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("APP_PORT", "8000")))
