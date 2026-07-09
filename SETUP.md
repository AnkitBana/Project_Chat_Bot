# Setup Guide

This guide will help you set up the AI Agent system step by step.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- At least one API key (OpenAI, Anthropic, or Google)

## Step-by-Step Installation

### 1. Verify Python Installation

```bash
python --version
# Should show Python 3.8 or higher
```

If Python is not installed, download it from [python.org](https://www.python.org/downloads/)

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- LangChain and provider integrations
- Vector stores (ChromaDB, FAISS)
- Web search tools
- File processing libraries
- API frameworks

### 4. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your favorite text editor
# Add your API keys
```

Example `.env` file:
```env
# Get your API keys from:
# OpenAI: https://platform.openai.com/api-keys
# Anthropic: https://console.anthropic.com/
# Google: https://makersuite.google.com/app/apikey

OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AI...

DEFAULT_LLM_PROVIDER=openai
```

### 5. Test Installation

Run the demo to verify everything works:

```bash
python main.py demo
```

You should see the agent perform various tasks.

## Getting API Keys

### OpenAI (GPT-4, GPT-3.5)

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy and paste into `.env`

**Note**: OpenAI requires payment setup for API access.

### Anthropic (Claude)

1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to API Keys
4. Create a new API key
5. Copy and paste into `.env`

### Google (Gemini)

1. Go to [Google AI Studio](https://makersuite.google.com/)
2. Sign in with Google account
3. Get API key
4. Copy and paste into `.env`

## Troubleshooting

### Import Errors

If you see import errors:
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### API Key Errors

Verify your API keys:
```python
from config import validate_api_keys
validate_api_keys()
```

### Permission Errors

On Windows, you might need to run as administrator.
On macOS/Linux, check file permissions:
```bash
chmod +x main.py
```

### Rate Limit Errors

If you hit rate limits:
- Wait a few minutes
- Use a different provider
- Upgrade your API plan

## Quick Start Commands

```bash
# Run demo
python main.py demo

# Single agent mode (interactive chat)
python main.py single

# Multi-agent mode
python main.py multi

# Run specific example
python examples.py 1  # Run example 1
python examples.py    # Run all examples
```

## Directory Structure After Setup

```
project_Agent/
├── agent.py
├── multi_agent.py
├── llm_provider.py
├── memory_manager.py
├── tools.py
├── config.py
├── main.py
├── examples.py
├── requirements.txt
├── .env                 # Your API keys (created by you)
├── .env.example
├── README.md
├── SETUP.md
├── .gitignore
├── data/               # Created automatically
│   ├── memory/
│   ├── files/
│   └── vector_store/
└── logs/               # Created automatically
    └── agent.log
```

## Next Steps

1. **Read the README.md** for detailed usage instructions
2. **Run examples.py** to see different capabilities
3. **Try the interactive chat** with `python main.py single`
4. **Experiment with multi-agent** using `python main.py multi`

## Common Use Cases

### Research Assistant
```bash
python main.py single
# Then ask: "Research the latest AI developments and summarize them"
```

### Code Helper
```python
from agent import AIAgent

agent = AIAgent(name="CodeHelper")
agent.run("Write a Python function to sort a list")
```

### Content Creation
```bash
python main.py multi
# Then: "Create a blog post about climate change"
```

## Performance Tips

1. **Use appropriate memory types**:
   - `buffer` for short conversations
   - `summary` for long conversations
   - `vector` for searchable history

2. **Choose the right provider**:
   - OpenAI: Best overall performance
   - Anthropic: Longer context, better reasoning
   - Google: Fast and cost-effective

3. **Optimize token usage**:
   - Lower temperature for factual tasks
   - Higher temperature for creative tasks
   - Adjust max_tokens based on needs

## Support

If you encounter issues:
1. Check this setup guide
2. Review the README.md
3. Verify your API keys
4. Check Python version compatibility
5. Ensure all dependencies are installed

## Security Notes

- Never commit `.env` file to version control
- Keep API keys secure
- Rotate keys regularly
- Monitor API usage and costs
- Use environment-specific keys for development/production

---

Happy coding with AI Agents! 🤖