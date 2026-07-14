"""
Example usage scenarios for the AI Agent system.
"""
from agent import AIAgent
from multi_agent import MultiAgentSystem, AgentRole
from config import setup_directories


def example_basic_agent():
    """Example 1: Basic agent usage."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Agent Usage")
    print("="*60 + "\n")
    
    # Create a simple agent
    agent = AIAgent(
        name="BasicAgent",
        verbose=False
    )
    
    # Ask a question
    response = agent.run("What is 15 * 23?")
    print(f"Q: What is 15 * 23?")
    print(f"A: {response}\n")
    
    # Get agent info
    info = agent.get_info()
    print(f"Agent Info:")
    print(f"  Provider: {info['provider']}")
    print(f"  Model: {info['model']}")
    print(f"  Tools: {len(info['tools'])}")


def example_web_search():
    """Example 2: Web search capabilities."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Web Search")
    print("="*60 + "\n")
    
    agent = AIAgent(name="SearchAgent", verbose=False)
    
    response = agent.run("Search for the latest news about artificial intelligence")
    print(f"Q: Search for the latest news about artificial intelligence")
    print(f"A: {response[:300]}...\n")


def example_file_operations():
    """Example 3: File operations."""
    print("\n" + "="*60)
    print("EXAMPLE 3: File Operations")
    print("="*60 + "\n")
    
    agent = AIAgent(name="FileAgent", verbose=False)
    
    # Write to file
    response = agent.run("Write 'Hello from AI Agent!' to a file called example_output.txt")
    print(f"Q: Write 'Hello from AI Agent!' to a file called example_output.txt")
    print(f"A: {response}\n")
    
    # Read from file
    response = agent.run("Read the contents of example_output.txt")
    print(f"Q: Read the contents of example_output.txt")
    print(f"A: {response}\n")


def example_memory_management():
    """Example 4: Memory management."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Memory Management")
    print("="*60 + "\n")
    
    agent = AIAgent(
        name="MemoryAgent",
        verbose=False
    )
    
    # Have a conversation
    agent.run("My name is Alice")
    agent.run("I like programming in Python")
    response = agent.run("What's my name and what do I like?")
    
    print("Conversation:")
    print("  User: My name is Alice")
    print("  User: I like programming in Python")
    print(f"  User: What's my name and what do I like?")
    print(f"  Agent: {response}\n")
    
    # Check memory stats
    stats = agent.get_memory_stats()
    print(f"Memory Stats:")
    print(f"  Messages: {stats['message_count']}")
    print(f"  Session ID: {stats['session_id']}\n")


def example_multi_provider():
    """Example 5: Using different LLM providers."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Multiple LLM Providers")
    print("="*60 + "\n")
    
    from llm_provider import LLMProvider
    
    # Check available providers
    available = LLMProvider.get_available_providers()
    print("Available Providers:")
    for provider, is_available in available.items():
        status = "✓" if is_available else "✗"
        print(f"  {status} {provider}")
    print()
    
    # Create agents with different providers (if available)
    if available.get("openai"):
        agent = AIAgent(provider="openai", verbose=False)
        response = agent.run("Say hello")
        print(f"OpenAI Agent: {response}\n")


def example_sequential_agents():
    """Example 6: Sequential multi-agent execution."""
    print("\n" + "="*60)
    print("EXAMPLE 6: Sequential Multi-Agent")
    print("="*60 + "\n")
    
    system = MultiAgentSystem(verbose=False)
    
    # Create a pipeline: Research → Analyze → Write
    result = system.run_sequential(
        task="What are the benefits of renewable energy?",
        agent_sequence=[
            AgentRole.RESEARCHER,
            AgentRole.ANALYST,
            AgentRole.WRITER
        ]
    )
    
    print("Task: What are the benefits of renewable energy?")
    print("\nAgent Pipeline: Researcher → Analyst → Writer\n")
    
    for agent_role, output in result["outputs"].items():
        print(f"{agent_role.upper()}:")
        print(f"{output[:200]}...\n")


def example_parallel_agents():
    """Example 7: Parallel multi-agent execution."""
    print("\n" + "="*60)
    print("EXAMPLE 7: Parallel Multi-Agent")
    print("="*60 + "\n")
    
    system = MultiAgentSystem(verbose=False)
    
    # Multiple agents analyze the same task
    result = system.run_parallel(
        task="Analyze the pros and cons of remote work",
        agent_roles=[
            AgentRole.ANALYST,
            AgentRole.CRITIC
        ]
    )
    
    print("Task: Analyze the pros and cons of remote work")
    print("\nParallel Agents: Analyst + Critic\n")
    
    for agent_role, output in result["outputs"].items():
        print(f"{agent_role.upper()}:")
        print(f"{output[:200]}...\n")


def example_coordinated_agents():
    """Example 8: Coordinated multi-agent execution."""
    print("\n" + "="*60)
    print("EXAMPLE 8: Coordinated Multi-Agent")
    print("="*60 + "\n")
    
    system = MultiAgentSystem(verbose=False)
    
    # Coordinator orchestrates the task
    result = system.run_coordinated(
        task="Create a brief guide on getting started with machine learning"
    )
    
    print("Task: Create a brief guide on getting started with machine learning")
    print("\nCoordinator orchestrating specialized agents...\n")
    print(f"Result:\n{result[:400]}...\n")


def example_custom_agent():
    """Example 9: Custom agent with specific role."""
    print("\n" + "="*60)
    print("EXAMPLE 9: Custom Specialized Agent")
    print("="*60 + "\n")
    
    custom_prompt = """You are a helpful coding assistant.
    You write clean, efficient, well-documented code in any language requested.
    Always follow the language's idiomatic style guidelines.
    Provide explanations for your code."""

    agent = AIAgent(
        name="CodingAssistant",
        system_message=custom_prompt,
        verbose=False
    )

    response = agent.run("Write a Python function to calculate fibonacci numbers")
    print("Q: Write a Python function to calculate fibonacci numbers")
    print(f"A: {response[:300]}...\n")


def example_api_integration():
    """Example 10: API integration."""
    print("\n" + "="*60)
    print("EXAMPLE 10: API Integration")
    print("="*60 + "\n")
    
    agent = AIAgent(name="APIAgent", verbose=False)
    
    # Make an API call (using a public API)
    response = agent.run(
        "Make a GET request to https://api.github.com/users/github and show me the response"
    )
    print("Q: Make a GET request to https://api.github.com/users/github")
    print(f"A: {response[:300]}...\n")


def run_all_examples():
    """Run all examples."""
    setup_directories()
    
    examples = [
        example_basic_agent,
        example_web_search,
        example_file_operations,
        example_memory_management,
        example_multi_provider,
        example_sequential_agents,
        example_parallel_agents,
        example_coordinated_agents,
        example_custom_agent,
        example_api_integration,
    ]
    
    print("\n" + "="*60)
    print("AI AGENT SYSTEM - EXAMPLES")
    print("="*60)
    
    for i, example in enumerate(examples, 1):
        try:
            example()
            input(f"\nPress Enter to continue to example {i+1}/{len(examples)}...")
        except KeyboardInterrupt:
            print("\n\nExamples interrupted by user.")
            break
        except Exception as e:
            print(f"\nError in example: {str(e)}")
            print("Continuing to next example...\n")
    
    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        examples_map = {
            "1": example_basic_agent,
            "2": example_web_search,
            "3": example_file_operations,
            "4": example_memory_management,
            "5": example_multi_provider,
            "6": example_sequential_agents,
            "7": example_parallel_agents,
            "8": example_coordinated_agents,
            "9": example_custom_agent,
            "10": example_api_integration,
        }
        
        if example_num in examples_map:
            setup_directories()
            examples_map[example_num]()
        else:
            print(f"Example {example_num} not found. Available: 1-10")
    else:
        run_all_examples()

# Made with Bob
