from src.safe_agent_guard.models import Action
from src.safe_agent_guard.policy import evaluate_action


def test_read_only_auto_allowed():
    action = Action(
        name="list_dir",
        kind="list_dir",
        path=".",
        description="List a local project directory",
    )
    decision = evaluate_action(action)
    assert decision.allowed is True
    assert decision.requires_approval is False


def test_safe_edit_allowed():
    action = Action(
        name="write_patch",
        kind="write_patch",
        path="./tmp/example.patch",
        description="Create a patch in a safe workspace",
        sandbox_only=True,
    )
    decision = evaluate_action(action)
    assert decision.allowed is True
    assert decision.requires_approval is False


def test_high_risk_requires_approval():
    action = Action(
        name="deploy",
        kind="deploy",
        path="/production",
        command="deploy --prod",
        description="Deploy to production",
        rollback_plan="revert last release",
    )
    decision = evaluate_action(action)
    assert decision.allowed is True
    assert decision.requires_approval is True
    assert decision.requires_sandbox is True
    assert decision.requires_rollback is True


def test_unauthorized_action_blocked():
    action = Action(
        name="credential_dump",
        kind="secret_access",
        description="Attempt to access protected secrets without authorization",
    )
    decision = evaluate_action(action)
    assert decision.allowed is False
