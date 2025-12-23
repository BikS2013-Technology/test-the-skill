# UV Python Tool Guide

**Date:** December 23, 2025

This guide explains how to use the UV tool to set up and manage virtual environments, install packages, and run Python applications.

---

## Table of Contents

1. [What is UV?](#what-is-uv)
2. [Installation](#installation)
3. [Python Version Management](#python-version-management)
4. [Virtual Environments](#virtual-environments)
5. [Project Management](#project-management)
6. [Dependency Management](#dependency-management)
7. [Running Python Scripts](#running-python-scripts)
8. [Tools and uvx](#tools-and-uvx)
9. [pip-Compatible Commands](#pip-compatible-commands)
10. [Building and Publishing Packages](#building-and-publishing-packages)
11. [Docker Integration](#docker-integration)
12. [Complete Workflow Examples](#complete-workflow-examples)
13. [Best Practices](#best-practices)
14. [Command Reference](#command-reference)

---

## What is UV?

UV is an extremely fast Python package and project manager written in Rust. It is designed to replace multiple tools:

| Traditional Tool | UV Equivalent |
|-----------------|---------------|
| pip | `uv pip install` |
| pip-tools | `uv pip compile` |
| pipx | `uvx` / `uv tool` |
| poetry/pipenv | `uv init`, `uv add`, `uv sync` |
| pyenv | `uv python` |
| virtualenv | `uv venv` |

### Key Benefits

- **10-100x faster** than pip and other tools
- **Single binary** - no Python required to install
- **Unified toolchain** - replaces multiple tools
- **Cross-platform** - works on Linux, macOS, and Windows
- **Automatic Python management** - downloads Python if needed

---

## Installation

### macOS and Linux

```bash
# Using curl (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Using Homebrew
brew install uv
```

### Windows

```powershell
# Using PowerShell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Using winget
winget install astral-sh.uv
```

### Shell Autocompletion

```bash
# Bash
echo 'eval "$(uv --generate-shell-completion bash)"' >> ~/.bashrc

# Zsh
echo 'eval "$(uv --generate-shell-completion zsh)"' >> ~/.zshrc

# Fish
echo 'uv --generate-shell-completion fish | source' > ~/.config/fish/completions/uv.fish
```

---

## Python Version Management

UV can manage Python installations, eliminating the need for pyenv.

### Install Python

```bash
# Install the latest Python version
uv python install

# Install a specific version
uv python install 3.12

# Install multiple versions
uv python install 3.11 3.12 3.13

# Install with default python/python3 symlinks
uv python install --default

# Install alternative implementations (PyPy)
uv python install pypy@3.10
```

### List Python Versions

```bash
# List all available and installed versions
uv python list
```

### Use Specific Python Version

```bash
# Run a command with a specific Python version
uv run --python 3.12 script.py

# Create a venv with a specific Python version
uv venv --python 3.11

# Execute Python directly
uvx python@3.12 -c "print('hello')"
```

### Reinstall Python

```bash
# Reinstall all uv-managed Python versions
uv python install --reinstall
```

---

## Virtual Environments

### Create Virtual Environment

```bash
# Create .venv in current directory (default)
uv venv

# Create with a custom name/path
uv venv my_env
uv venv /path/to/env

# Create with specific Python version
uv venv --python 3.12

# Seed with pip (for pip magics in Jupyter)
uv venv --seed
```

### Activation (Optional)

**Important:** When using UV, you don't need to activate the virtual environment. UV automatically finds and uses `.venv` in the working directory or parent directories.

However, if you need to activate manually:

```bash
# macOS/Linux
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (CMD)
.venv\Scripts\activate.bat
```

### Using Virtual Environment Without Activation

```bash
# UV commands automatically use .venv
uv pip install requests    # Installs to .venv
uv run script.py           # Runs with .venv Python

# Direct execution
.venv/bin/python script.py
.venv/bin/pip list
```

---

## Project Management

UV provides a modern project workflow similar to Poetry or npm.

### Initialize a New Project

```bash
# Create a basic application project
uv init my-project
cd my-project

# Create in current directory
uv init

# Create a library (with build system)
uv init --lib my-library

# Create a packaged application
uv init --package my-app
```

### Project Structure

After `uv init`, you get:

```
my-project/
├── .python-version      # Python version pin
├── .venv/               # Virtual environment (created on first run)
├── README.md
├── main.py              # Entry point (for apps)
└── pyproject.toml       # Project configuration
```

### pyproject.toml Examples

**Basic Application:**
```toml
[project]
name = "example-app"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.11"
dependencies = []
```

**Library with Build System:**
```toml
[project]
name = "example-lib"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.11"
dependencies = []

[build-system]
requires = ["uv_build>=0.9.18,<0.10.0"]
build-backend = "uv_build"
```

**Packaged Application with Entry Points:**
```toml
[project]
name = "example-pkg"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.11"
dependencies = []

[project.scripts]
example-pkg = "example_pkg:main"

[build-system]
requires = ["uv_build>=0.9.18,<0.10.0"]
build-backend = "uv_build"
```

---

## Dependency Management

### Add Dependencies

```bash
# Add a package
uv add requests

# Add with version constraint
uv add 'flask>=2.0'
uv add 'django>=4.0,<5.0'

# Add multiple packages
uv add requests flask sqlalchemy
```

### Add Development Dependencies

```bash
# Add to dev dependency group
uv add --dev pytest pytest-cov black mypy

# Add to custom group
uv add --group docs sphinx sphinx-rtd-theme
uv add --group test pytest hypothesis
```

### Add from Various Sources

```bash
# From Git repository
uv add git+https://github.com/encode/httpx
uv add git+https://github.com/encode/httpx --tag 0.27.0
uv add git+https://github.com/encode/httpx --branch main
uv add git+ssh://git@github.com/user/repo.git

# From local path
uv add ./local-package
uv add ~/projects/my-lib/

# Editable install (for development)
uv add --editable ./my-local-package

# From URL
uv add "https://files.pythonhosted.org/packages/.../httpx-0.27.0.tar.gz"
```

### Add Platform-Specific Dependencies

```bash
# Only on Linux
uv add "jax; sys_platform == 'linux'"

# Only for Python 3.11+
uv add "numpy; python_version >= '3.11'"
```

### Remove Dependencies

```bash
# Remove a package
uv remove requests

# Remove multiple packages
uv remove requests flask
```

### Migrate from requirements.txt

```bash
# Add all packages from requirements.txt
uv add -r requirements.txt

# Add with constraints
uv add -r requirements.txt -c constraints.txt
```

### Lock Dependencies

```bash
# Create/update lockfile (uv.lock)
uv lock

# Check if lockfile is up-to-date
uv lock --check

# Upgrade all packages to latest versions
uv lock --upgrade

# Upgrade specific package
uv lock --upgrade-package requests
```

### Sync Environment

```bash
# Sync environment to match lockfile
uv sync

# Sync without updating lockfile
uv sync --frozen

# Error if lockfile is out of date
uv sync --locked

# Include optional dependencies
uv sync --extra docs
uv sync --all-extras

# Include dependency groups
uv sync --group dev
uv sync --group test

# Keep extraneous packages
uv sync --inexact
```

### pyproject.toml with Dependencies

```toml
[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.100.0",
    "pydantic>=2.0",
    "sqlalchemy>=2.0",
]

[project.optional-dependencies]
docs = ["sphinx", "sphinx-rtd-theme"]

[dependency-groups]
dev = ["pytest", "pytest-cov", "black", "mypy"]
test = ["pytest", "hypothesis"]
```

---

## Running Python Scripts

### Basic Script Execution

```bash
# Run a script in project context
uv run script.py

# Run with arguments
uv run script.py arg1 arg2 --flag

# Run Python module
uv run -m pytest

# Run with specific Python version
uv run --python 3.12 script.py
```

### Run Without Project Dependencies

```bash
# Skip project dependency installation
uv run --no-project script.py
```

### Run with Ad-hoc Dependencies

```bash
# Install dependencies just for this run
uv run --with requests script.py
uv run --with 'pandas>=2.0' --with numpy analysis.py
```

### Run from stdin

```bash
# Pipe script to uv
echo 'print("hello")' | uv run -

# Heredoc
uv run - <<EOF
import sys
print(sys.version)
EOF
```

### Inline Script Metadata

For scripts with dependencies, use inline metadata:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "requests>=2.28",
#     "rich",
# ]
# ///

import requests
from rich import print

response = requests.get("https://api.github.com")
print(response.json())
```

Then run:

```bash
uv run script.py  # Dependencies are installed automatically
```

---

## Tools and uvx

UV can run command-line tools from Python packages without permanent installation.

### Run Tools with uvx

```bash
# Run a tool (installed temporarily)
uvx ruff check .
uvx black --check .
uvx mypy src/

# Run specific version
uvx ruff@0.6.0 --version

# Run latest version (bypass cache)
uvx ruff@latest --version

# Run in isolated environment
uvx --isolated ruff --version

# Run from specific package
uvx --from httpie http GET https://api.github.com
```

### Install Tools Permanently

```bash
# Install tool globally
uv tool install ruff
uv tool install black
uv tool install httpie

# Install with version constraint
uv tool install 'ruff>=0.6.0'

# Install from Git
uv tool install git+https://github.com/astral-sh/ruff

# Install with extra dependencies
uv tool install mkdocs --with mkdocs-material

# Verify installation
ruff --version
```

### Manage Installed Tools

```bash
# List installed tools
uv tool list

# Upgrade a tool
uv tool upgrade ruff

# Upgrade all tools
uv tool upgrade --all

# Uninstall a tool
uv tool uninstall ruff

# Update shell PATH
uv tool update-shell
```

---

## pip-Compatible Commands

UV provides pip-compatible commands for familiar workflows.

### Install Packages

```bash
# Install packages
uv pip install requests
uv pip install 'flask>=2.0'
uv pip install requests flask sqlalchemy

# Install from requirements.txt
uv pip install -r requirements.txt

# Install from pyproject.toml
uv pip install -r pyproject.toml
uv pip install -r pyproject.toml --extra dev

# Install in editable mode
uv pip install -e .
uv pip install -e ./my-package

# Install to system Python (use with caution)
uv pip install --system requests
```

### Uninstall Packages

```bash
# Uninstall packages
uv pip uninstall requests
uv pip uninstall requests flask

# Uninstall from requirements file
uv pip uninstall -r requirements.txt
```

### List and Show Packages

```bash
# List installed packages
uv pip list

# Show package details
uv pip show requests

# Check for outdated packages
uv pip list --outdated
```

### Compile Requirements

```bash
# Compile requirements.in to requirements.txt
uv pip compile requirements.in -o requirements.txt

# With constraints
uv pip compile requirements.in -c constraints.txt -o requirements.txt

# Universal (cross-platform) resolution
uv pip compile --universal requirements.in -o requirements.txt

# Upgrade all packages
uv pip compile --upgrade requirements.in -o requirements.txt
```

### Sync Environment

```bash
# Sync to requirements.txt (exact match)
uv pip sync requirements.txt

# Sync to lockfile
uv pip sync pylock.toml
```

### Freeze

```bash
# Output installed packages
uv pip freeze > requirements.txt
```

---

## Building and Publishing Packages

### Build Package

```bash
# Build both sdist and wheel
uv build

# Build only source distribution
uv build --sdist

# Build only wheel
uv build --wheel

# Build specific package in workspace
uv build --package my-package

# Build without uv.sources (for publishing)
uv build --no-sources
```

Output goes to `dist/` directory:
```
dist/
├── my_package-0.1.0-py3-none-any.whl
└── my_package-0.1.0.tar.gz
```

### Publish Package

```bash
# Publish to PyPI (uses keyring or prompts for credentials)
uv publish

# Publish with token
uv publish --token $PYPI_TOKEN

# Publish specific files
uv publish dist/*.whl

# Publish to custom index
uv publish --publish-url https://upload.pypi.org/legacy/
```

### Configure Publishing in pyproject.toml

```toml
[[tool.uv.index]]
name = "private-registry"
url = "https://my-registry.com/simple/"
publish-url = "https://my-registry.com/upload/"
```

---

## Docker Integration

### Basic Dockerfile

```dockerfile
FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application
COPY . .

# Run application
CMD ["uv", "run", "python", "main.py"]
```

### With Virtual Environment

```dockerfile
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Create and use virtual environment
RUN uv venv /opt/venv
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy and run application
COPY . .
CMD ["python", "main.py"]
```

### Optimized Multi-Stage Build

```dockerfile
# Build stage
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Runtime stage
FROM python:3.12-slim

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY . .
CMD ["python", "main.py"]
```

---

## Complete Workflow Examples

### Example 1: New Web Application Project

```bash
# Create project
uv init my-web-app
cd my-web-app

# Add dependencies
uv add fastapi uvicorn sqlalchemy alembic
uv add --dev pytest pytest-asyncio httpx black mypy

# Create application structure
mkdir -p src/my_web_app tests

# Run development server
uv run uvicorn src.my_web_app.main:app --reload

# Run tests
uv run pytest

# Run type checking
uv run mypy src/

# Format code
uv run black src/ tests/
```

### Example 2: Data Science Project

```bash
# Create project
uv init data-analysis
cd data-analysis

# Add data science dependencies
uv add pandas numpy matplotlib seaborn scikit-learn
uv add --dev jupyter jupyterlab ipykernel

# Create virtual environment with pip for Jupyter
uv venv --seed

# Install Jupyter
uv pip install jupyterlab

# Start Jupyter
uv run jupyter lab
```

### Example 3: CLI Tool Development

```bash
# Create packaged application
uv init --package my-cli-tool
cd my-cli-tool

# Add dependencies
uv add click rich
uv add --dev pytest

# Edit pyproject.toml to add entry point
# [project.scripts]
# my-cli = "my_cli_tool:main"

# Build and test
uv build
uv run my-cli --help

# Publish
uv publish
```

### Example 4: Working with Existing Project

```bash
# Clone existing project
git clone https://github.com/user/project.git
cd project

# Install dependencies from lockfile
uv sync

# Or if migrating from requirements.txt
uv add -r requirements.txt
uv add -r requirements-dev.txt --dev

# Run the application
uv run python main.py
```

---

## Best Practices

### 1. Always Use Virtual Environments

```bash
# UV creates .venv automatically, but you can be explicit
uv venv
uv sync
```

### 2. Pin Python Version

Create `.python-version` file:
```
3.12
```

Or in `pyproject.toml`:
```toml
[project]
requires-python = ">=3.11,<3.13"
```

### 3. Commit Lock Files

Always commit `uv.lock` to version control for reproducible builds:
```bash
git add uv.lock
git commit -m "Update dependencies"
```

### 4. Use Dependency Groups

```toml
[project]
dependencies = ["fastapi", "sqlalchemy"]

[dependency-groups]
dev = ["pytest", "black", "mypy"]
docs = ["sphinx", "sphinx-rtd-theme"]
```

### 5. Use Frozen/Locked in CI/CD

```bash
# CI should fail if lockfile is out of date
uv sync --locked

# Or use frozen to skip lockfile check
uv sync --frozen
```

### 6. Prefix Python Commands with `uv run`

```bash
# Instead of activating venv
uv run python script.py
uv run pytest
uv run black .

# Or use source activation per CLAUDE.md instructions
source .venv/bin/activate && python script.py
```

### 7. Use uvx for One-Off Tools

```bash
# Don't pollute project with tools
uvx black --check .
uvx ruff check .
uvx mypy src/
```

---

## Command Reference

### Project Commands

| Command | Description |
|---------|-------------|
| `uv init` | Initialize new project |
| `uv add <pkg>` | Add dependency |
| `uv add --dev <pkg>` | Add dev dependency |
| `uv remove <pkg>` | Remove dependency |
| `uv lock` | Create/update lockfile |
| `uv sync` | Sync environment to lockfile |
| `uv run <cmd>` | Run command in project context |

### Python Management

| Command | Description |
|---------|-------------|
| `uv python install` | Install Python |
| `uv python list` | List Python versions |
| `uv venv` | Create virtual environment |

### Tool Management

| Command | Description |
|---------|-------------|
| `uvx <tool>` | Run tool temporarily |
| `uv tool install <pkg>` | Install tool permanently |
| `uv tool list` | List installed tools |
| `uv tool upgrade <pkg>` | Upgrade tool |
| `uv tool uninstall <pkg>` | Uninstall tool |

### pip-Compatible Commands

| Command | Description |
|---------|-------------|
| `uv pip install <pkg>` | Install package |
| `uv pip uninstall <pkg>` | Uninstall package |
| `uv pip list` | List packages |
| `uv pip freeze` | Output installed packages |
| `uv pip compile` | Compile requirements |
| `uv pip sync` | Sync to requirements |

### Build & Publish

| Command | Description |
|---------|-------------|
| `uv build` | Build package |
| `uv publish` | Publish to PyPI |

---

## Summary

UV provides a unified, fast, and modern Python development experience:

1. **Install UV** → `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. **Create Project** → `uv init my-project`
3. **Add Dependencies** → `uv add requests flask`
4. **Run Code** → `uv run python main.py`
5. **Sync Environment** → `uv sync`

For virtual environment activation as per your CLAUDE.md configuration:
```bash
source .venv/bin/activate && python script.py
```

Or let UV handle it automatically:
```bash
uv run python script.py
```
