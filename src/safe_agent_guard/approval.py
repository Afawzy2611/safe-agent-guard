from .models import Action, ApprovalDecision


class ApprovalGate:
    def request_approval(self, action: Action) -> ApprovalDecision:
        print("\n=== HIGH-RISK ACTION DETECTED ===")
        print(f"Action: {action.name}")
        print(f"Kind: {action.kind}")
        print(f"Path: {action.path}")
        print(f"Command: {action.command}")
        print(f"Description: {action.description}")
        print("This action requires explicit approval.")
        print("Risk controls: approval required, sandbox required, rollback required.")

        response = input("Approve this action? [y/N]: ").strip().lower()

        if response in {"y", "yes"}:
            return ApprovalDecision(
                approved=True,
                action_name=action.name,
                reason="User explicitly approved the high-risk action.",
            )

        return ApprovalDecision(
            approved=False,
            action_name=action.name,
            reason="User rejected the high-risk action.",
        )
