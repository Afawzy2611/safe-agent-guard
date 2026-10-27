from typing import Set

from .models import Action, PolicyDecision, RiskLevel


DENYLIST: Set[str] = {
    "exploit",
    "credential_dump",
    "unauthorized_network_scan",
    "malware_generation",
    "unauthorized_access",
    "tamper_with_production",
    "bypass_approval",
}


def classify_risk(action: Action) -> RiskLevel:
    if action.kind in {"read_file", "search", "list_dir", "summarize", "inspect"}:
        return RiskLevel.READ_ONLY
    if action.kind in {"create_draft", "write_patch", "generate_doc", "generate_report"}:
        return RiskLevel.SAFE_EDIT
    if action.kind in {"edit_file", "run_tests", "lint_project"}:
        return RiskLevel.MODERATE
    if action.kind in {"git_push", "deploy", "database_migration", "service_restart"}:
        return RiskLevel.HIGH
    if action.kind in {"delete_file", "delete_dir", "rm_rf", "format_disk"}:
        return RiskLevel.DESTRUCTIVE
    if action.kind in {"secret_access", "secret_rotation", "cloud_write", "publish_release"}:
        return RiskLevel.SECRET
    return RiskLevel.MODERATE


def evaluate_action(action: Action) -> PolicyDecision:
    if action.name in DENYLIST:
        return PolicyDecision(
            allowed=False,
            reason="Blocked by policy: unauthorized or malicious action",
            risk_level=RiskLevel.SECRET,
        )

    risk = classify_risk(action)

    if risk == RiskLevel.READ_ONLY:
        return PolicyDecision(
            allowed=True,
            requires_approval=False,
            requires_sandbox=False,
            requires_rollback=False,
            reason="Read-only action is auto-allowed.",
            risk_level=risk,
        )

    if risk == RiskLevel.SAFE_EDIT:
        return PolicyDecision(
            allowed=True,
            requires_approval=False,
            requires_sandbox=bool(action.sandbox_only),
            requires_rollback=False,
            reason="Safe edit is allowed.",
            risk_level=risk,
        )

    if risk in {RiskLevel.MODERATE, RiskLevel.HIGH, RiskLevel.DESTRUCTIVE, RiskLevel.SECRET}:
        return PolicyDecision(
            allowed=True,
            requires_approval=True,
            requires_sandbox=True,
            requires_rollback=(risk in {RiskLevel.HIGH, RiskLevel.DESTRUCTIVE, RiskLevel.SECRET}),
            reason="This action is risky and requires approval and sandboxing.",
            risk_level=risk,
        )

    return PolicyDecision(
        allowed=False,
        reason="Action is not permitted by policy.",
        risk_level=risk,
    )
