# Quick Start Guide

Get up and running with the AI Agent system in 5 minutes!

## 1. Install (2 minutes)

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

## 2. Configure (1 minute)

Edit `.env` and add at least one API key:

```env
OPENAI_API_KEY=your_key_here
# OR
ANTHROPIC_API_KEY=your_key_here
# OR
GOOGLE_API_KEY=your_key_here
```

## 3. Run (2 minutes)

### Option A: Quick Demo
```bash
python main.py demo
```

### Option B: Interactive Chat
```bash
python main.py single
```

### Option C: Multi-Agent System
```bash
python main.py multi
```

## Basic Usage Examples

### Simple Agent
```python
from agent import AIAgent

agent = AIAgent()
response = agent.run("What is 25 * 47?")
print(response)
```

### Agent with Memory
```python
agent = AIAgent(memory_type="buffer")
agent.run("My name is Alice")
agent.run("I like Python")
response = agent.run("What's my name?")
# Response: "Your name is Alice"
```

### Web Search
```python
agent = AIAgent()
response = agent.run("Search for latest AI news")
```

### File Operations
```python
agent = AIAgent()
agent.run("Write 'Hello World' to hello.txt")
agent.run("Read hello.txt")
```

### Multi-Agent
```python
from multi_agent import MultiAgentSystem, AgentRole

system = MultiAgentSystem()
result = system.run_coordinated(
    "Research AI trends and write a summary"
)
```

## Common Commands

```bash
# Run demo
python main.py demo

# Interactive single agent
python main.py single

# Multi-agent system
python main.py multi

# Run examples
python examples.py

# Run specific example
python examples.py 1
```

## Key Features at a Glance

| Feature | Description | Example |
|---------|-------------|---------|
| **Multi-Provider** | OpenAI, Anthropic, Google | `provider="openai"` |
| **Memory** | Buffer, Summary, Vector | `memory_type="buffer"` |
| **Web Search** | DuckDuckGo integration | "Search for..." |
| **File Ops** | Read/Write files | "Write to file.txt" |
| **API Calls** | HTTP requests | "Call API endpoint" |
| **Multi-Agent** | Specialized agents | `AgentRole.RESEARCHER` |

## Configuration Options

```python
agent = AIAgent(
    name="MyAgent",           # Agent name
    provider="openai",        # openai, anthropic, google
    model="gpt-4",           # Model name
    temperature=0.7,         # 0.0-1.0
    memory_type="buffer",    # buffer, summary, vector
    verbose=True             # Show detailed output
)
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Import errors | `pip install -r requirements.txt` |
| API key error | Check `.env` file |
| Rate limit | Wait or switch provider |
| Memory error | Use `summary` or `vector` memory |

## Next Steps

1. ✅ Read [README.md](README.md) for detailed documentation
2. ✅ Check [SETUP.md](SETUP.md) for installation help
3. ✅ Run [examples.py](examples.py) to see all features
4. ✅ Build your own agent!

## Quick Tips

💡 **Use the right memory type**
- Short chats: `buffer`
- Long chats: `summary`
- Searchable: `vector`

💡 **Choose your provider wisely**
- Best overall: OpenAI
- Long context: Anthropic
- Cost-effective: Google

💡 **Leverage tools**
- Web search for current info
- File ops for persistence
- API calls for integrations

## Example Workflows

### Research Assistant
```python
agent = AIAgent(name="Researcher")
agent.run("Research quantum computing and save to research.txt")
```

### Code Helper
```python
agent = AIAgent(name="Coder")
agent.run("Write a Python function to calculate fibonacci")
```

### Content Creator
```python
system = MultiAgentSystem()
system.run_coordinated("Create a blog post about AI")
```

---

**Ready to build?** Start with `python main.py demo` 🚀