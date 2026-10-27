from .approval import ApprovalGate
from .models import Action, AuditEntry, ExecutionResult, RiskLevel
from .policy import evaluate_action
from .sandbox import SandboxRunner


class AgentRunner:
    def __init__(self):
        self.approval_gate = ApprovalGate()
        self.sandbox_runner = SandboxRunner()
        self.audit_log = []

    def execute(self, action: Action) -> ExecutionResult:
        decision = evaluate_action(action)

        if not decision.allowed:
            self.audit_log.append(
                AuditEntry(
                    action_name=action.name,
                    risk_level=decision.risk_level or RiskLevel.MODERATE,
                    status="blocked",
                    reason=decision.reason,
                    approved=False,
                    sandbox_used=False,
                    rollback_used=False,
                )
            )
            return ExecutionResult(
                success=False,
                status="blocked",
                output="Action blocked by policy.",
                reason=decision.reason,
            )

        if decision.requires_approval:
            approval = self.approval_gate.request_approval(action)
            if not approval.approved:
                self.audit_log.append(
                    AuditEntry(
                        action_name=action.name,
                        risk_level=decision.risk_level or RiskLevel.MODERATE,
                        status="rejected",
                        reason=approval.reason,
                        approved=False,
                        sandbox_used=decision.requires_sandbox,
                        rollback_used=decision.requires_rollback,
                    )
                )
                return ExecutionResult(
                    success=False,
                    status="rejected",
                    output="Action rejected by user.",
                    reason=approval.reason,
                )

            action.user_approved = True

        if decision.requires_sandbox:
            context = self.sandbox_runner.create_context(action.path or ".")
            sandbox_dir = self.sandbox_runner.prepare(context, action.path or ".")
            self.audit_log.append(
                AuditEntry(
                    action_name=action.name,
                    risk_level=decision.risk_level or RiskLevel.MODERATE,
                    status="executed_in_sandbox",
                    reason="Approved risky action executed in sandbox.",
                    approved=action.user_approved,
                    sandbox_used=True,
                    rollback_used=decision.requires_rollback,
                    details={"sandbox_dir": sandbox_dir},
                )
            )
            return ExecutionResult(
                success=True,
                status="executed_in_sandbox",
                output=f"Action {action.name} executed in sandbox at {sandbox_dir}.",
            )

        self.audit_log.append(
            AuditEntry(
                action_name=action.name,
                risk_level=decision.risk_level or RiskLevel.MODERATE,
                status="executed",
                reason="Low-risk action executed automatically.",
                approved=action.user_approved,
                sandbox_used=False,
                rollback_used=False,
            )
        )
        return ExecutionResult(
            success=True,
            status="executed",
            output=f"Action {action.name} executed automatically.",
        )
