import os
from typing import Optional

from openai import OpenAI

from src.safe_agent_guard.models import Action


class OpenAIAgentRuntime:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def build_default_action(self, user_task: str, requested_kind: Optional[str] = None) -> Action:
        task = user_task.strip()
        kind = (requested_kind or "search").lower()

        if "deploy" in task.lower() or kind == "deploy":
            return Action(
                name="deploy_release",
                kind="deploy",
                path="/production",
                command="deploy --prod",
                description="Deploy a release to production after approval.",
                rollback_plan="restore previous build and revert config",
            )

        if "patch" in task.lower() or "edit" in task.lower() or kind == "edit":
            return Action(
                name="draft_patch",
                kind="write_patch",
                path="./tmp/draft.patch",
                description="Generate a patch draft in a sandboxed work area.",
                sandbox_only=True,
            )

        if "test" in task.lower() or kind == "test":
            return Action(
                name="run_tests",
                kind="run_tests",
                path=".",
                description="Run a test suite in a controlled environment.",
                sandbox_only=True,
            )

        return Action(
            name="inspect_repo",
            kind="search",
            path=".",
            description="Inspect the repository and identify task-relevant files.",
        )

    def plan_action(self, user_task: str, requested_kind: Optional[str] = None) -> Action:
        if not self.client:
            return self.build_default_action(user_task, requested_kind)

        try:
            prompt = (
                "You are a policy-aware agent planner for a safe automation system. "
                "Return only a JSON object with fields: action_name, action_kind, path, description, sandbox_only, rollback_plan. "
                "Choose from: search, write_patch, run_tests, deploy. "
                "Do not add any extra commentary."
            )
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_task},
                ],
                temperature=0.2,
            )
            raw = response.choices[0].message.content or ""
            lower = raw.lower()

            if "deploy" in lower:
                return Action(
                    name="deploy_release",
                    kind="deploy",
                    path="/production",
                    command="deploy --prod",
                    description="Deploy a release to production after approval.",
                    rollback_plan="restore previous build and revert config",
                )

            if "patch" in lower or "edit" in lower:
                return Action(
                    name="draft_patch",
                    kind="write_patch",
                    path="./tmp/draft.patch",
                    description="Generate a patch draft in a sandboxed work area.",
                    sandbox_only=True,
                )

            if "test" in lower:
                return Action(
                    name="run_tests",
                    kind="run_tests",
                    path=".",
                    description="Run local tests in a controlled environment.",
                    sandbox_only=True,
                )

            return self.build_default_action(user_task, requested_kind)
        except Exception:
            return self.build_default_action(user_task, requested_kind)
