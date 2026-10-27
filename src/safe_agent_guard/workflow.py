from .models import Action
from .runner import AgentRunner


class Workflow:
    def __init__(self):
        self.runner = AgentRunner()

    def build_actions(self):
        return [
            Action(
                name="search_codebase",
                kind="search",
                path=".",
                description="Search the repository for relevant code and instructions.",
            ),
            Action(
                name="draft_patch",
                kind="write_patch",
                path="./tmp/generated_patch.diff",
                description="Create a draft patch in a structured folder.",
                sandbox_only=True,
            ),
            Action(
                name="deploy_to_prod",
                kind="deploy",
                path="/production",
                command="deploy --prod",
                description="Deploy approved changes to production.",
                rollback_plan="revert previous release and restore config snapshot",
            ),
        ]

    def run(self):
        for action in self.build_actions():
            result = self.runner.execute(action)
            print(f"[{result.status}] {result.output}")
            if not result.success:
                print(f"Reason: {result.reason}")
                break
