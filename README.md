# AURA

AURA is a personal desktop AI assistant for Windows, built with Python 3.12 and PySide6.

## Current status

The desktop shell includes an assistant panel and a conversation view. Chat requests can be sent to either a local Ollama model or the OpenAI API. For Ollama, the optional Thinking checkbox selects between a normal instruct model and a separate reasoning-capable model. Voice, persistent memory, screen perception and Windows automation are planned for later stages.

## Requirements

- Windows 10/11
- Python 3.12
- Git
- Ollama (for local AI) or an OpenAI API key (for cloud AI)

## Setup

Activate the virtual environment and install the project:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

If the environment does not exist yet:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## Configure AI

Copy the example environment file:

```powershell
Copy-Item .env.example .env
```

### Local models (default)

1. Install and start [Ollama](https://ollama.com/).
2. Download both models:

```powershell
ollama pull qwen3:4b-instruct
ollama pull qwen3:4b
```

3. Configure `.env`:

```dotenv
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:4b-instruct
OLLAMA_THINKING_MODEL=qwen3:4b
AI_MAX_TOKENS=800
AI_THINKING_MAX_TOKENS=1600
AI_TIMEOUT=300
```

The **Thinking** checkbox selects the model for each request:
- Off: `OLLAMA_MODEL` (default `qwen3:4b-instruct`) for everyday responses.
- On: `OLLAMA_THINKING_MODEL` (default `qwen3:4b`) for reasoning tasks.

Generation limits are configured independently: `AI_MAX_TOKENS` defaults to 800 for normal mode, while `AI_THINKING_MAX_TOKENS` defaults to 1600 for Thinking mode. Both accept values from 1 to 8192. This gives the reasoning model more room for internal thinking before it produces the final answer. You can replace either model name with another compatible Ollama model. The timeout can be adjusted with `AI_TIMEOUT` (1-900 seconds; default 300).

### OpenAI API

Set these values in `.env`:

```dotenv
AI_PROVIDER=openai
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-4o-mini
```

Keep the API key private. Never commit `.env` or real credentials.

## Run

```powershell
python -m aura
```

## Tests and lint

```powershell
python -m pytest
ruff check .
ruff format --check .
```
