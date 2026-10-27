from .models import Action
from .runner import AgentRunner


class AgentRuntime:
    def __init__(self):
        self.runner = AgentRunner()

    def plan_actions(self, task: str):
        action_map = {
            "inspect": Action(
                name="inspect_repo",
                kind="search",
                path=".",
                description="Inspect repository structure and find relevant files.",
            ),
            "draft": Action(
                name="draft_patch",
                kind="write_patch",
                path="./tmp/draft.patch",
                sandbox_only=True,
                description="Generate a patch draft in a sandboxed working directory.",
            ),
            "deploy": Action(
                name="deploy_release",
                kind="deploy",
                path="/production",
                command="deploy --prod",
                description="Deploy a release to production.",
                rollback_plan="restore previous build and revert config",
            ),
        }

        if task == "inspect":
            return [action_map["inspect"]]
        if task == "draft":
            return [action_map["inspect"], action_map["draft"]]
        if task == "deploy":
            return [action_map["inspect"], action_map["draft"], action_map["deploy"]]

        return [action_map["inspect"]]

    def run_task(self, task: str):
        for action in self.plan_actions(task):
            result = self.runner.execute(action)
            print(f"[{result.status}] {result.output}")
            if not result.success:
                print(f"Reason: {result.reason}")
                break
