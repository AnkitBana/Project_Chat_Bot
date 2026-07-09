"""
Main entry point for the AI Agent system.
Usage:
    python main.py demo
    python main.py single
    python main.py multi
"""
import sys
import argparse
sys.stdout.reconfigure(encoding="utf-8")
from agent import AIAgent
from multi_agent import MultiAgentSystem, AgentRole
from config import setup_directories, validate_api_keys


def run_demo():
    """Run a quick self-contained demo."""
    print("\n" + "="*60)
    print("  AI AGENT — Demo Mode")
    print("="*60)

    validate_api_keys()
    setup_directories()

    agent = AIAgent(name="Demo Agent", verbose=False)
    info = agent.get_info()
    print(f"\nProvider : {info['provider']}")
    print(f"Model    : {info['model']}")
    print(f"Tools    : {len(info['tools'])}\n")

    tests = [
        "What is 123 * 456?",
        "What is today's date and time?",
        "Write 'Hello from AI Agent!' to demo_output.txt and confirm.",
    ]
    for q in tests:
        # Fresh agent per question so memory doesn't accumulate
        fresh = AIAgent(name="Demo Agent", verbose=False)
        print(f"Q: {q}")
        print(f"A: {fresh.run(q)}\n")

    print("Demo complete! [OK]\n")


def run_single():
    """Interactive single-agent chat."""
    print("\n" + "="*60)
    print("  AI AGENT — Interactive Chat")
    print("="*60)

    validate_api_keys()
    setup_directories()

    agent = AIAgent(verbose=True)
    info = agent.get_info()
    print(f"\nProvider: {info['provider']}  Model: {info['model']}")
    agent.chat()


def run_multi():
    """Interactive multi-agent mode."""
    print("\n" + "="*60)
    print("  AI AGENT — Multi-Agent Mode")
    print("="*60)

    validate_api_keys()
    setup_directories()

    system = MultiAgentSystem(verbose=True)
    print("\nEnter a complex task. Type 'exit' to quit.\n")

    while True:
        task = input("Task: ").strip()
        if not task:
            continue
        if task.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        print("\nRunning coordinated agents...\n")
        result = system.run_coordinated(task)
        print("\n" + "="*60)
        print("FINAL RESULT")
        print("="*60)
        print(result)
        print()


def main():
    parser = argparse.ArgumentParser(description="AI Agent System")
    parser.add_argument(
        "mode",
        choices=["demo", "single", "multi"],
        help="demo | single | multi",
    )
    args = parser.parse_args()

    try:
        if args.mode == "demo":
            run_demo()
        elif args.mode == "single":
            run_single()
        elif args.mode == "multi":
            run_multi()
    except ValueError as e:
        print(f"\nConfiguration error: {e}")
        print("Add your API key to the .env file and try again.")
    except KeyboardInterrupt:
        print("\nInterrupted.")


if __name__ == "__main__":
    main()
