"""
Optimized AI Agent using more LangChain built-in features.
This version is more concise and leverages LangChain's abstractions better.
"""
from typing import Optional, List, Dict, Any
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.callbacks import StreamingStdOutCallbackHandler
from llm_provider import LLMProvider
from tools import get_tools
from config import setup_directories


class OptimizedAgent:
    """
    Optimized AI Agent using LangChain's built-in agent initialization.
    More concise and leverages LangChain abstractions better.
    """
    
    def __init__(
        self,
        name: str = "Assistant",
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        agent_type: AgentType = AgentType.OPENAI_FUNCTIONS,
        verbose: bool = True,
        streaming: bool = False
    ):
        """
        Initialize optimized agent.
        
        Args:
            name: Agent name
            provider: LLM provider
            model: Model name
            temperature: Generation temperature
            agent_type: LangChain agent type
            verbose: Enable verbose output
            streaming: Enable streaming responses
        """
        setup_directories()
        
        self.name = name
        self.verbose = verbose
        
        # Get LLM with optional streaming
        callbacks = [StreamingStdOutCallbackHandler()] if streaming else None
        self.llm = LLMProvider.get_llm(
            provider=provider,
            model=model,
            temperature=temperature,
            streaming=streaming,
            callbacks=callbacks
        )
        
        # Initialize memory using LangChain's built-in
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Get tools
        self.tools = get_tools()
        
        # Initialize agent using LangChain's factory
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=agent_type,
            memory=self.memory,
            verbose=verbose,
            handle_parsing_errors=True,
            max_iterations=10
        )
    
    def run(self, query: str) -> str:
        """Run agent with query."""
        try:
            result = self.agent.run(query)
            return result
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def arun(self, query: str) -> str:
        """Async run."""
        try:
            result = await self.agent.arun(query)
            return result
        except Exception as e:
            return f"Error: {str(e)}"
    
    def chat(self):
        """Interactive chat."""
        print(f"\n{self.name}: Hello! How can I help you?")
        print("(Type 'exit' to quit)\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                if not user_input or user_input.lower() in ['exit', 'quit', 'bye']:
                    print(f"\n{self.name}: Goodbye!")
                    break
                
                response = self.run(user_input)
                print(f"\n{self.name}: {response}\n")
            except KeyboardInterrupt:
                print(f"\n\n{self.name}: Goodbye!")
                break


# Convenience function for quick agent creation
def create_agent(
    provider: str = "openai",
    **kwargs
) -> OptimizedAgent:
    """
    Quick agent creation with sensible defaults.
    
    Usage:
        agent = create_agent()
        agent.run("What is 2+2?")
    """
    return OptimizedAgent(provider=provider, **kwargs)

# Made with Bob
