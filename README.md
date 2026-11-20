# AURA

AURA is a personal desktop AI assistant for Windows, built with Python 3.12 and PySide6.

## Current status

The first desktop UI shell includes an assistant/avatar placeholder, a conversation panel, and a message input. The reply is currently a placeholder; AI, voice, memory, screen perception and Windows automation are not connected yet.

## Requirements

- Windows 10/11
- Python 3.12
- Git

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

## Run

```powershell
python -m aura
```

## Tests and lint

```powershell
python -m pytest
ruff check .
```

Copy `.env.example` to `.env` before configuring optional AI providers. Never commit real API keys or credentials.
