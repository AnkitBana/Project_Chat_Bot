# How to Run the AI Agent System

## Quick Start (3 Steps)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Set Up API Key
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your API key
# Use any text editor (notepad, vim, nano, etc.)
```

Add at least ONE API key to `.env`:
```env
OPENAI_API_KEY=sk-your-key-here
```

### Step 3: Run!
```bash
# Option 1: Quick Demo
python main.py demo

# Option 2: Interactive Chat
python main.py single

# Option 3: Multi-Agent System
python main.py multi
```

---

## Detailed Instructions

### 1️⃣ Install Python Dependencies

Open terminal/command prompt in the project folder and run:

```bash
pip install -r requirements.txt
```

This installs all required libraries (LangChain, OpenAI, etc.)

**Troubleshooting:**
- If `pip` not found, try `pip3` or `python -m pip`
- On Windows, you might need to run as Administrator
- If errors occur, try: `pip install --upgrade pip` first

---

### 2️⃣ Get API Keys

You need at least ONE API key from:

#### Option A: OpenAI (Recommended)
1. Go to https://platform.openai.com/
2. Sign up or log in
3. Go to API Keys section
4. Click "Create new secret key"
5. Copy the key (starts with `sk-`)

#### Option B: Anthropic (Claude)
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Get API key from settings
4. Copy the key (starts with `sk-ant-`)

#### Option C: Google (Gemini)
1. Go to https://makersuite.google.com/
2. Sign in with Google
3. Get API key
4. Copy the key

---

### 3️⃣ Configure Environment

**On Windows:**
```bash
copy .env.example .env
notepad .env
```

**On Mac/Linux:**
```bash
cp .env.example .env
nano .env
```

Edit the `.env` file and paste your API key:
```env
# Add your key here (remove the # comment)
OPENAI_API_KEY=sk-your-actual-key-here

# Or use Anthropic
# ANTHROPIC_API_KEY=sk-ant-your-key-here

# Or use Google
# GOOGLE_API_KEY=your-google-key-here

# Set which provider to use
DEFAULT_LLM_PROVIDER=openai
```

Save and close the file.

---

### 4️⃣ Run the Agent

#### Option 1: Quick Demo (Recommended First)
```bash
python main.py demo
```

This runs a quick demonstration showing:
- Basic calculations
- Web search
- File operations
- Memory usage

#### Option 2: Interactive Chat
```bash
python main.py single
```

Start chatting with the AI agent:
```
You: What is the capital of France?
Assistant: The capital of France is Paris.

You: Search for latest AI news
Assistant: [Performs web search and shows results]

You: exit
```

#### Option 3: Multi-Agent System
```bash
python main.py multi
```

Use multiple specialized agents:
```
Task: Research electric vehicles and write a summary
[System uses Researcher → Analyst → Writer agents]
```

#### Option 4: Run Examples
```bash
# Run all examples
python examples.py

# Run specific example (1-10)
python examples.py 1
```

---

## Usage Examples

### Example 1: Simple Question
```bash
python main.py single
```
```
You: What is 15 * 23?
Assistant: 15 * 23 = 345
```

### Example 2: Web Search
```bash
python main.py single
```
```
You: Search for the latest developments in quantum computing
Assistant: [Searches web and provides results]
```

### Example 3: File Operations
```bash
python main.py single
```
```
You: Write "Hello World" to test.txt
Assistant: Successfully wrote to test.txt

You: Read test.txt
Assistant: Hello World
```

### Example 4: Complex Task (Multi-Agent)
```bash
python main.py multi
```
```
Task: Create a business plan for a coffee shop
[Coordinator assigns to Planner → Analyst → Writer]
```

---

## Programmatic Usage

### Basic Script
Create a file `my_agent.py`:

```python
from agent import AIAgent

# Create agent
agent = AIAgent(name="MyBot")

# Ask questions
response = agent.run("What is Python?")
print(response)

# Use tools
response = agent.run("Search for Python tutorials")
print(response)
```

Run it:
```bash
python my_agent.py
```

### With Memory
```python
from agent import AIAgent

agent = AIAgent(memory_type="buffer")

# Have a conversation
agent.run("My name is Alice")
agent.run("I like programming")
response = agent.run("What's my name?")
print(response)  # "Your name is Alice"
```

### Multi-Agent
```python
from multi_agent import MultiAgentSystem, AgentRole

system = MultiAgentSystem()

result = system.run_coordinated(
    "Research AI trends and write a report"
)
print(result)
```

---

## Common Issues & Solutions

### Issue 1: "Module not found"
**Solution:**
```bash
pip install -r requirements.txt
```

### Issue 2: "API key not found"
**Solution:**
- Check `.env` file exists
- Verify API key is correct
- Make sure no extra spaces in `.env`

### Issue 3: "Rate limit exceeded"
**Solution:**
- Wait a few minutes
- Use a different provider
- Check your API usage limits

### Issue 4: "Permission denied"
**Solution:**
- On Windows: Run as Administrator
- On Mac/Linux: Use `sudo` or check file permissions

### Issue 5: Import errors after installation
**Solution:**
```bash
# Reinstall with force
pip install -r requirements.txt --force-reinstall

# Or use virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## Testing Your Setup

Run this quick test:

```bash
python -c "from agent import AIAgent; print('✅ Setup successful!')"
```

If you see "✅ Setup successful!", you're ready to go!

---

## Next Steps

1. ✅ **Start with demo**: `python main.py demo`
2. ✅ **Try interactive chat**: `python main.py single`
3. ✅ **Read documentation**: Check `README.md`
4. ✅ **Run examples**: `python examples.py`
5. ✅ **Build your own**: Create custom agents!

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `python main.py demo` | Quick demonstration |
| `python main.py single` | Interactive chat |
| `python main.py multi` | Multi-agent system |
| `python examples.py` | Run all examples |
| `python examples.py 1` | Run example #1 |

---

## Need Help?

1. Check `SETUP.md` for detailed setup
2. Check `README.md` for full documentation
3. Check `QUICKSTART.md` for quick reference
4. Check `OPTIMIZATION.md` for performance tips

---

**Ready? Let's go!** 🚀

```bash
python main.py demo