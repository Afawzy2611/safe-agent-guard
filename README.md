# Safe Agent Guard

A production-style, approval-gated agent runtime for authorized risky actions.

## What it does

- runs low-risk tasks automatically
- blocks unauthorized or harmful actions with policy checks
- requires explicit approval for high-risk actions
- executes risky actions in a sandbox
- requires rollback planning for destructive operations
- records all actions for auditability
- integrates with OpenAI for task planning and policy-aware action selection
- includes a lightweight FastAPI approval dashboard

## Core components

- openai-agents-python: agent orchestration
- failproofai: policy enforcement
- AgentOps-Control-Center: observability and audit logs
- personal-ai-assistant: user approval UI
- skills/plugins: reusable capabilities
- OpenAI runtime: policy-aware planning and action generation
- FastAPI approval UI: interactive task approval flow

## Safety model

This project is designed for authorized automation only.

Allowed:
- read/search tasks
- local drafts and patch generation
- sandboxed local edits
- controlled tests
- approved deployment or config changes after explicit approval

Blocked:
- malicious or unauthorized actions
- exploitation or credential theft
- destructive actions without approval
- privileged operations outside the approved sandbox

## Quick start

1. Create a virtual environment
2. Install dependencies:
   pip install -r requirements.txt
3. Set your OpenAI key if you want runtime planning:
   export OPENAI_API_KEY="your_key_here"
4. Run the app:
   python app.py
5. Open the browser at http://localhost:8000

## Example flow

1. Agent plans an action
2. Policy engine checks risk
3. Low-risk actions run automatically
4. High-risk actions stop and ask for approval
5. A sandbox is created for risky execution
6. Rollback plan is enforced if required
7. Logs are stored for audit
8. Approval UI surfaces actions and allows human confirmation

## New features in this release

- real OpenAI planning support via `openai` SDK
- built-in FastAPI approval dashboard
- structured task approval flow
- environment-based configuration
- sandbox-aware execution pipeline

## Notes

This project is intentionally strict by default. It fails closed.
