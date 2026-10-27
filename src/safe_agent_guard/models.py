from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class RiskLevel(str, Enum):
    READ_ONLY = "read_only"
    SAFE_EDIT = "safe_edit"
    MODERATE = "moderate"
    HIGH = "high"
    DESTRUCTIVE = "destructive"
    SECRET = "secret"


@dataclass
class Action:
    name: str
    kind: str
    path: Optional[str] = None
    command: Optional[str] = None
    description: str = ""
    sandbox_only: bool = False
    requires_approval: bool = False
    rollback_plan: Optional[str] = None
    user_approved: bool = False


@dataclass
class PolicyDecision:
    allowed: bool
    requires_approval: bool = False
    requires_sandbox: bool = False
    requires_rollback: bool = False
    reason: str = ""
    risk_level: Optional[RiskLevel] = None


@dataclass
class ApprovalDecision:
    approved: bool
    reason: str = ""
    action_name: str = ""


@dataclass
class SandboxContext:
    working_dir: str
    temp_dir: Optional[str] = None
    copy_to_temp: bool = True
    rollback_script: Optional[str] = None


@dataclass
class ExecutionResult:
    success: bool
    status: str
    output: str = ""
    reason: str = ""


@dataclass
class AuditEntry:
    action_name: str
    risk_level: RiskLevel
    status: str
    reason: str = ""
    approved: bool = False
    sandbox_used: bool = False
    rollback_used: bool = False
    details: Dict[str, Any] = field(default_factory=dict)
