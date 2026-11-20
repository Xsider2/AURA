# AURA

AURA is a personal desktop AI assistant for Windows, built with Python 3.12 and PySide6.

## Current status

The desktop shell includes an assistant panel and a conversation view. Chat requests can be sent to either a local Ollama model or the OpenAI API. Voice, persistent memory, screen perception and Windows automation are planned for later stages.

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

### Local model (default)

1. Install and start [Ollama](https://ollama.com/).
2. Download a model, for example:

```powershell
ollama pull llama3.2
```

3. Keep these settings in `.env`:

```dotenv
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

You can select another model already installed in Ollama by changing `OLLAMA_MODEL`.

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
