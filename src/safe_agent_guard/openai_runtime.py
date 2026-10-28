import os
from typing import Dict

from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from src.safe_agent_guard.models import Action
from src.safe_agent_guard.policy import evaluate_action
from src.safe_agent_guard.openai_runtime import OpenAIAgentRuntime

app = FastAPI(title=os.getenv("APP_TITLE", "Safe Agent Guard"))
agent_runtime = OpenAIAgentRuntime(api_key=os.getenv("OPENAI_API_KEY"))

TASKS: Dict[str, Dict[str, object]] = {}


class TaskCreateRequest(BaseModel):
    task: str
    requested_kind: str | None = None


class TaskDecisionRequest(BaseModel):
    approved: bool


def render_dashboard() -> str:
    return """
    <html>
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />
        <title>Safe Agent Guard</title>
        <style>
          :root {
            --bg: #0b1020;
            --panel: #111827;
            --card: #0f172a;
            --border: #374151;
            --text: #e5e7eb;
            --muted: #94a3b8;
            --primary: #2563eb;
            --primary-strong: #1d4ed8;
            --success: #22c55e;
            --warning: #f59e0b;
            --danger: #ef4444;
          }
          * { box-sizing: border-box; }
          html, body {
            margin: 0;
            padding: 0;
            background: var(--bg);
            color: var(--text);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
          }
          body {
            min-height: 100vh;
            display: flex;
            justify-content: center;
            padding: 18px;
          }
          .shell {
            width: min(100%, 980px);
          }
          .panel {
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
          }
          h1 {
            margin: 0 0 8px;
            font-size: clamp(1.8rem, 5vw, 2.4rem);
          }
          p {
            color: var(--muted);
            margin: 0 0 16px;
          }
          form {
            display: grid;
            gap: 12px;
          }
          label {
            display: block;
            font-size: 0.88rem;
            color: var(--muted);
            margin-bottom: 6px;
          }
          input, select, textarea, button {
            width: 100%;
            border-radius: 12px;
            border: 1px solid var(--border);
            background: #0f172a;
            color: var(--text);
            font-size: 1rem;
            padding: 14px 12px;
          }
          textarea {
            min-height: 120px;
            resize: vertical;
          }
          button {
            background: var(--primary);
            border: none;
            cursor: pointer;
            font-weight: 700;
            min-height: 46px;
            transition: background 0.2s ease;
          }
          button:hover {
            background: var(--primary-strong);
          }
          .quick-row {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 8px;
            margin-bottom: 14px;
          }
          .quick-row button {
            background: #1e293b;
            border: 1px solid var(--border);
            font-size: 0.9rem;
            padding: 12px 10px;
          }
          .result-grid {
            margin-top: 18px;
            display: grid;
            gap: 14px;
          }
          .task-card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 14px;
          }
          .task-card h3 {
            margin: 0 0 8px;
            font-size: 1.05rem;
          }
          .meta {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 12px;
          }
          .pill {
            background: rgba(37,99,235,0.15);
            border: 1px solid rgba(96,165,250,0.25);
            color: #bfdbfe;
            border-radius: 999px;
            padding: 6px 10px;
            font-size: 0.78rem;
          }
          .pill.success { background: rgba(34,197,94,0.12); color: #bbf7d0; border-color: rgba(34,197,94,0.25); }
          .pill.warning { background: rgba(245,158,11,0.12); color: #fcd34d; border-color: rgba(245,158,11,0.25); }
          .pill.danger { background: rgba(239,68,68,0.12); color: #fecaca; border-color: rgba(239,68,68,0.25); }
          .approve-row {
            display: flex;
            gap: 8px;
            margin-top: 12px;
          }
          .approve-row button {
            flex: 1;
          }
          .approve-row .approve {
            background: var(--success);
          }
          .approve-row .reject {
            background: var(--danger);
          }
          @media (max-width: 640px) {
            body { padding: 12px; }
            .panel { padding: 14px; }
            .quick-row { grid-template-columns: 1fr; }
            .approve-row { flex-direction: column; }
            input, select, textarea, button { font-size: 16px; }
          }
        </style>
      </head>
      <body>
        <div class="shell">
          <div class="panel">
            <h1>Safe Agent Guard</h1>
            <p>Mobile-friendly, approval-gated automation for safe and authorized actions.</p>

            <div class="quick-row">
              <button type="button" onclick="setQuick('inspect')">Inspect</button>
              <button type="button" onclick="setQuick('draft')">Draft</button>
              <button type="button" onclick="setQuick('deploy')">Deploy</button>
            </div>

            <form id="task-form" method="post" action="/api/tasks">
              <div>
                <label for="task">Task</label>
                <textarea id="task" name="task" placeholder="Describe the task you want the agent to handle..."></textarea>
              </div>
              <div>
                <label for="requested_kind">Kind</label>
                <select id="requested_kind" name="requested_kind">
                  <option value="search">Search</option>
                  <option value="edit">Edit</option>
                  <option value="test">Test</option>
                  <option value="deploy">Deploy</option>
                </select>
              </div>
              <button type="submit">Create task</button>
            </form>
          </div>

          <div class="result-grid" id="task-list">
            <div class="task-card">
              <h3>Task queue</h3>
              <p>Tasks will appear here after you create them.</p>
            </div>
          </div>
        </div>

        <script>
          function setQuick(kind) {
            const textarea = document.getElementById('task');
            const select = document.getElementById('requested_kind');
            if (kind === 'inspect') {
              textarea.value = 'Inspect the repository and identify the relevant files for this request.';
              select.value = 'search';
            } else if (kind === 'draft') {
              textarea.value = 'Draft a safe patch for the requested change and keep it sandboxed.';
              select.value = 'edit';
            } else if (kind === 'deploy') {
              textarea.value = 'Prepare the production deployment and require approval before executing.';
              select.value = 'deploy';
            }
            textarea.focus();
          }

          async function refreshTasks() {
            const res = await fetch('/api/tasks');
            const data = await res.json();
            const list = document.getElementById('task-list');
            list.innerHTML = '';

            if (!data.tasks || data.tasks.length === 0) {
              list.innerHTML = '<div class="task-card"><h3>Task queue</h3><p>No tasks yet.</p></div>';
              return;
            }

            for (const item of data.tasks) {
              const card = document.createElement('div');
              card.className = 'task-card';
              card.innerHTML = `
                <h3>${item.action}</h3>
                <div class="meta">
                  <span class="pill ${item.status === 'approved' ? 'success' : item.status === 'rejected' ? 'danger' : 'warning'}">${item.status}</span>
                  <span class="pill">Task ${item.task_id}</span>
                </div>
                <p>${item.task}</p>
                ${item.status === 'pending' ? `
                  <div class="approve-row">
                    <button class="approve" type="button" onclick="approveTask('${item.task_id}', true)">Approve</button>
                    <button class="reject" type="button" onclick="approveTask('${item.task_id}', false)">Reject</button>
                  </div>` : ''}
              `;
              list.appendChild(card);
            }
          }

          async function approveTask(taskId, approved) {
            const formData = new FormData();
            formData.append('approved', approved ? 'true' : 'false');
            await fetch(`/api/tasks/${taskId}/approve`, {
              method: 'POST',
              body: formData,
            });
            refreshTasks();
          }

          document.getElementById('task-form').addEventListener('submit', async (event) => {
            event.preventDefault();
            const formData = new FormData(event.target);
            const res = await fetch('/api/tasks', {
              method: 'POST',
              body: formData,
            });
            const data = await res.json();
            if (data.task_id) {
              event.target.reset();
              refreshTasks();
            }
          });

          refreshTasks();
        </script>
      </body>
    </html>
    """


@app.get("/", response_class=HTMLResponse)
async def index():
    return render_dashboard()


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
    return {
        "tasks": [{
            "task_id": task_id,
            "status": record["status"],
            "task": record["task"],
            "action": record["action"].name,
        } for task_id, record in TASKS.items()]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("APP_PORT", "8000")))
