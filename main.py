from src.safe_agent_guard.workflow import Workflow
from src.safe_agent_guard.agent_runtime import AgentRuntime


def main():
    print("Safe Agent Guard")
    print("Choose a mode:")
    print("1. run demo workflow")
    print("2. inspect")
    print("3. draft")
    print("4. deploy")
    print("0. exit")

    choice = input("Select: ").strip()

    if choice == "1":
        workflow = Workflow()
        workflow.run()
    elif choice == "2":
        runtime = AgentRuntime()
        runtime.run_task("inspect")
    elif choice == "3":
        runtime = AgentRuntime()
        runtime.run_task("draft")
    elif choice == "4":
        runtime = AgentRuntime()
        runtime.run_task("deploy")
    else:
        print("Exiting.")


if __name__ == "__main__":
    main()
