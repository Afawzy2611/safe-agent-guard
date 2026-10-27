import os
import shutil
import tempfile

from .models import ExecutionResult, SandboxContext


class SandboxRunner:
    def create_context(self, working_dir: str) -> SandboxContext:
        temp_dir = tempfile.mkdtemp(prefix="safe_agent_guard_")
        return SandboxContext(
            working_dir=working_dir,
            temp_dir=temp_dir,
            copy_to_temp=True,
            rollback_script=f"{temp_dir}/rollback.sh",
        )

    def prepare(self, context: SandboxContext, source_dir: str) -> str:
        sandbox_dir = os.path.join(context.temp_dir, "sandbox")
        if os.path.exists(source_dir):
            shutil.copytree(source_dir, sandbox_dir, dirs_exist_ok=True)
        else:
            os.makedirs(sandbox_dir, exist_ok=True)
        return sandbox_dir

    def rollback(self, context: SandboxContext) -> ExecutionResult:
        if context.temp_dir and os.path.exists(context.temp_dir):
            shutil.rmtree(context.temp_dir, ignore_errors=True)
        return ExecutionResult(
            success=True,
            status="rolled_back",
            output="Sandbox cleanup complete.",
        )
