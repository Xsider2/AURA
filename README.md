# AURA

AURA is a personal desktop AI assistant for Windows, built with Python 3.12 and PySide6.

## Current status

The repository currently contains the first desktop UI shell:

- a main window with an assistant/avatar placeholder;
- a conversation panel;
- a message input with Enter and button submission;
- a safe text-to-HTML boundary for user messages.

The assistant response is intentionally a placeholder. AI, voice, memory, screen perception and Windows automation are not connected yet.

## Requirements

- Windows 10/11
- Python 3.12
- Git

## Setup

From the repository root, activate the virtual environment and install the project:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

If the virtual environment has not been created yet:

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

## Configuration

Copy `.env.example` to `.env` before configuring optional AI providers. Never commit real API keys or credentials.
