# LangGraph CLI Guide

A comprehensive guide to using the LangGraph Command Line Interface (CLI) for building, developing, and deploying LangGraph applications.

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Configuration File (langgraph.json)](#configuration-file-langgraphjson)
4. [CLI Commands](#cli-commands)
   - [langgraph dev](#langgraph-dev)
   - [langgraph build](#langgraph-build)
   - [langgraph up](#langgraph-up)
   - [langgraph dockerfile](#langgraph-dockerfile)
   - [langgraph deploy](#langgraph-deploy)
5. [Application Structure](#application-structure)
6. [Docker Deployment](#docker-deployment)
7. [Testing Your Application](#testing-your-application)
8. [LangGraph Platform Deployment](#langgraph-platform-deployment)

---

## Overview

The LangGraph CLI is a command-line tool for building, running, and deploying LangGraph Platform API servers. It provides commands for:

- **Development**: Run a local development server with hot reloading
- **Building**: Create Docker images for deployment
- **Deployment**: Deploy to the LangGraph Platform or self-hosted environments

The CLI supports both **Python** and **JavaScript/TypeScript** projects.

---

## Installation

### Prerequisites

- **Docker**: Required for `build` and `up` commands
- **Python 3.11+**: Required for Python projects
- **UV**: Recommended Python package manager ([install UV](https://docs.astral.sh/uv/getting-started/installation/))
- **Node.js 20+**: Required for JavaScript projects

### Python Installation

```bash
# Basic installation
uv add langgraph-cli

# With in-memory support (required for 'dev' command)
uv add "langgraph-cli[inmem]"
```

> **Note**: If you're not using UV, you can alternatively use pip:
> ```bash
> pip install -U "langgraph-cli[inmem]"
> ```

### JavaScript Installation

```bash
# Using npx (no installation required)
npx @langchain/langgraph-cli --help

# Global installation
npm install -g @langchain/langgraph-cli
```

### Verify Installation

```bash
# Python
langgraph --help

# JavaScript
npx @langchain/langgraph-cli --help
```

---

## Configuration File (langgraph.json)

The `langgraph.json` file is the central configuration file for your LangGraph application. It declares dependencies, graphs, and environment variables.

### Basic Structure

```json
{
  "dependencies": ["./my_agent"],
  "graphs": {
    "agent": "./my_agent/agent.py:graph"
  },
  "env": ".env"
}
```

### Configuration Options

| Key | Description | Example |
|-----|-------------|---------|
| `dependencies` | List of local packages and external libraries | `[".", "langchain_openai"]` |
| `graphs` | Map of graph names to their entry points | `{"agent": "./src/agent.py:graph"}` |
| `env` | Path to environment file or inline variables | `".env"` or `{"API_KEY": "xxx"}` |
| `auth` | Custom authentication handler | `{"path": "./auth.py:my_auth"}` |
| `node_version` | Node.js version (JS projects only) | `"20"` |
| `dockerfile_lines` | Additional Dockerfile instructions | `[]` |
| `image_distro` | Base image distribution (`wolfi` for smaller images) | `"wolfi"` |

### Python Example

```json
{
  "dependencies": ["langchain_openai", "./your_package"],
  "graphs": {
    "my_agent": "./your_package/your_file.py:agent"
  },
  "env": "./.env",
  "image_distro": "wolfi"
}
```

> **Security Recommendation**: Use `"image_distro": "wolfi"` for production deployments. [Wolfi](https://wolfi.dev/) is a security-oriented, minimal Linux distribution designed for containers that provides:
> - Smaller image sizes (faster deployments)
> - Fewer vulnerabilities (minimal attack surface)
> - Regular security updates

### JavaScript Example

```json
{
  "node_version": "20",
  "dockerfile_lines": [],
  "dependencies": ["."],
  "graphs": {
    "agent": "./src/agent.ts:graph"
  },
  "env": ".env"
}
```

### With Custom Authentication

```json
{
  "dependencies": ["."],
  "graphs": {
    "agent": "./my_agent/agent.py:graph"
  },
  "env": ".env",
  "auth": {
    "path": "./auth.py:my_auth"
  }
}
```

### Monorepo Configuration

For monorepos with shared packages:

```json
{
  "dependencies": [
    ".",
    "../../shared-utils"
  ],
  "graphs": {
    "customer_support": "./agent/graph.py:graph"
  },
  "env": ".env"
}
```

---

## CLI Commands

### langgraph dev

Runs the LangGraph API server in **development mode** with hot reloading. This is a lightweight server that does not require Docker.

```bash
langgraph dev [OPTIONS]
```

#### Options

| Option | Default | Description |
|--------|---------|-------------|
| `-c, --config FILE` | `langgraph.json` | Path to configuration file |
| `--host TEXT` | `127.0.0.1` | Host to bind the server to |
| `--port INTEGER` | `2024` | Port to bind the server to |
| `--no-reload` | - | Disable auto-reload |
| `--n-jobs-per-worker INTEGER` | `10` | Number of jobs per worker |
| `--debug-port INTEGER` | - | Port for debugger to listen on |
| `--wait-for-client` | `False` | Wait for debugger client before starting |
| `--no-browser` | - | Skip auto-opening browser |
| `--studio-url TEXT` | `https://smith.langchain.com` | LangGraph Studio URL |
| `--allow-blocking` | `False` | Allow synchronous I/O blocking operations |
| `--tunnel` | `False` | Expose via public Cloudflare tunnel |

#### Examples

```bash
# Basic development server
langgraph dev

# Custom port and host
langgraph dev --port 3000 --host 0.0.0.0

# With debugging
langgraph dev --debug-port 5678 --wait-for-client

# Disable hot reload
langgraph dev --no-reload

# JavaScript
npx @langchain/langgraph-cli dev
```

---

### langgraph build

Builds a Docker image for the LangGraph Platform API server.

```bash
langgraph build [OPTIONS]
```

#### Options

| Option | Description |
|--------|-------------|
| `-t, --tag TEXT` | Tag for the Docker image (required) |
| `--platform TEXT` | Target platform(s) (e.g., `linux/amd64,linux/arm64`) |
| `--pull` | Pull the latest remote Docker image |
| `--no-pull` | Use locally built images |
| `-c, --config FILE` | Path to configuration file |
| `--build-command TEXT` | Custom build command (JS projects) |
| `--install-command TEXT` | Custom install command (JS projects) |

#### Examples

```bash
# Basic build
langgraph build -t my-agent-image

# Multi-platform build
langgraph build --platform linux/amd64,linux/arm64 -t my-image --pull

# JavaScript with custom commands
langgraph build -t my-image --no-pull \
  --build-command "yarn run turbo build" \
  --install-command "yarn install"
```

---

### langgraph up

Starts the LangGraph API server locally within a Docker container. Requires Docker to be running.

```bash
langgraph up [OPTIONS]
```

#### Options

| Option | Description |
|--------|-------------|
| `--port INTEGER` | Port to bind the server to |
| `--postgres-uri TEXT` | PostgreSQL connection URI |
| `--watch` | Watch for file changes |
| `--verbose` | Enable verbose logging |
| `--no-pull` | Don't pull latest images |
| `--recreate` | Recreate containers |
| `-d TEXT` | Docker compose file |

#### Examples

```bash
# Basic startup
langgraph up

# With custom PostgreSQL and port
langgraph up --port 8000 \
  --postgres-uri "postgresql://user:password@host:port/database" \
  --watch --verbose

# With docker-compose file
langgraph up --no-pull --recreate -d docker-compose.yml
```

---

### langgraph dockerfile

Generates a Dockerfile for building a LangGraph Platform API server Docker image.

```bash
langgraph dockerfile [OPTIONS] OUTPUT_FILE
```

#### Examples

```bash
# Generate Dockerfile
langgraph dockerfile -c langgraph.json Dockerfile
```

> **Note**: Re-run this command after updating your `langgraph.json` configuration.

---

### langgraph deploy

Deploys your application to the LangGraph Platform.

```bash
langgraph deploy --config langgraph.json
```

---

## Application Structure

A typical LangGraph application has the following structure:

### Python Project

```
my-langgraph-app/
├── my_agent/
│   ├── __init__.py
│   └── agent.py          # Contains your graph
├── langgraph.json        # Configuration file
├── requirements.txt      # Python dependencies
├── pyproject.toml        # (Alternative) Project configuration
└── .env                  # Environment variables
```

### JavaScript Project

```
my-langgraph-app/
├── src/
│   └── agent.ts          # Contains your graph
├── langgraph.json        # Configuration file
├── package.json          # Node.js dependencies
└── .env                  # Environment variables
```

### Python Dependencies

When using UV (recommended), initialize your project and add the required dependencies:

```bash
# Initialize project
uv init

# Create virtual environment
uv venv

# Add core dependencies
uv add "langgraph-cli[inmem]" langgraph langchain-openai

# Add development dependencies
uv add --dev pytest python-dotenv
```

This creates a `pyproject.toml` with the following dependencies:

```toml
[project]
name = "my-langgraph-app"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "langgraph-cli[inmem]>=0.4.0",
    "langgraph>=1.0.0",
    "langchain-openai>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=9.0.0",
    "python-dotenv>=1.0.0",
]
```

Alternatively, if using `requirements.txt`:

```
langgraph-cli[inmem]>=0.4.0
langgraph>=1.0.0
langchain-openai>=1.0.0
python-dotenv>=1.0.0
```

### JavaScript Dependencies

For JavaScript/TypeScript projects, your `package.json` should include:

```json
{
  "name": "my-langgraph-app",
  "version": "1.0.0",
  "type": "module",
  "dependencies": {
    "@langchain/langgraph": "^0.2.0",
    "@langchain/openai": "^0.3.0",
    "zod": "^3.23.0"
  },
  "devDependencies": {
    "@langchain/langgraph-cli": "^0.0.1",
    "typescript": "^5.0.0",
    "vitest": "^2.0.0"
  }
}
```

### Environment Variables Configuration

Proper environment variable management is critical for LangGraph applications. The `.env` file contains sensitive credentials and configuration settings.

**Example .env File:**

```bash
# LLM Provider Configuration
# Choose ONE of the following configurations:

# Option 1: OpenAI
OPENAI_API_KEY=sk-your-openai-api-key-here

# Option 2: Azure OpenAI
AZURE_OPENAI_API_KEY=your-azure-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT=your-deployment-name

# LangSmith (optional but recommended for tracing)
LANGSMITH_API_KEY=your-langsmith-api-key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=my-langgraph-project
```

**Best Practices:**

1. **Never commit `.env` files** - Add `.env` to your `.gitignore`
2. **Validate required variables** - Check for missing credentials at startup
3. **Use environment-specific files** - `.env.development`, `.env.production`
4. **Document required variables** - Create a `.env.example` template

**Environment Variable Validation Pattern:**

```python
import os

def validate_env_vars(required_vars: list[str]) -> None:
    """
    Validate that all required environment variables are set.

    Raises:
        ValueError: If any required variable is missing.
    """
    missing = [var for var in required_vars if not os.environ.get(var)]
    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}"
        )

# Usage at application startup
validate_env_vars([
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_API_VERSION",
    "AZURE_OPENAI_DEPLOYMENT",
])
```

### Example Agent File (Python)

```python
# my_agent/agent.py
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

class MyState(TypedDict):
    messages: list

def agent_node(state: MyState):
    # Your agent logic here
    return {"messages": state["messages"] + ["Hello from agent!"]}

# Create the graph
builder = StateGraph(MyState)
builder.add_node("agent", agent_node)
builder.add_edge(START, "agent")
builder.add_edge("agent", END)

# Compile the graph - this is what langgraph.json references
graph = builder.compile()
```

### Example Agent with Azure OpenAI

For enterprise environments using Azure OpenAI, here's how to configure your agent:

**Environment Variables (.env)**

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
```

**Agent Implementation (my_agent/azure_agent.py)**

```python
# my_agent/azure_agent.py
import os
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import AzureChatOpenAI


class AgentState(TypedDict):
    """State definition for the agent graph with message handling."""
    messages: Annotated[list, add_messages]


def get_azure_llm() -> AzureChatOpenAI:
    """
    Create and return an Azure OpenAI chat model.

    Raises:
        ValueError: If required environment variables are not set.
    """
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION")
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT")

    if not api_key:
        raise ValueError("AZURE_OPENAI_API_KEY environment variable is not set")
    if not endpoint:
        raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is not set")
    if not api_version:
        raise ValueError("AZURE_OPENAI_API_VERSION environment variable is not set")
    if not deployment:
        raise ValueError("AZURE_OPENAI_DEPLOYMENT environment variable is not set")

    return AzureChatOpenAI(
        azure_endpoint=endpoint,
        azure_deployment=deployment,
        api_version=api_version,
        api_key=api_key,
    )


def chatbot_node(state: AgentState) -> dict:
    """Chatbot node that uses Azure OpenAI to generate responses."""
    llm = get_azure_llm()
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


# Create the graph
builder = StateGraph(AgentState)
builder.add_node("chatbot", chatbot_node)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

# Compile the graph
azure_graph = builder.compile()
```

**langgraph.json for Azure Agent**

```json
{
  "dependencies": ["./my_agent"],
  "graphs": {
    "azure_agent": "./my_agent/azure_agent.py:azure_graph"
  },
  "env": ".env"
}
```

---

## Docker Deployment

### Self-Hosted Deployment with Docker Compose

Create a `docker-compose.yml` file:

```yaml
volumes:
  langgraph-data:
    driver: local

services:
  langgraph-redis:
    image: redis:6
    healthcheck:
      test: redis-cli ping
      interval: 5s
      timeout: 1s
      retries: 5

  langgraph-postgres:
    image: postgres:16
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: postgres
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - langgraph-data:/var/lib/postgresql/data
    healthcheck:
      test: pg_isready -U postgres
      start_period: 10s
      timeout: 1s
      retries: 5
      interval: 5s

  langgraph-api:
    image: ${IMAGE_NAME}
    ports:
      - "8123:8000"
    depends_on:
      langgraph-redis:
        condition: service_healthy
      langgraph-postgres:
        condition: service_healthy
    env_file:
      - .env
    environment:
      REDIS_URI: redis://langgraph-redis:6379
      LANGSMITH_API_KEY: ${LANGSMITH_API_KEY}
      DATABASE_URI: postgres://postgres:postgres@langgraph-postgres:5432/postgres?sslmode=disable
```

### Deploy with Docker Compose

```bash
# Build the image first
langgraph build -t my-langgraph-app

# Set the image name
export IMAGE_NAME=my-langgraph-app

# Start services
docker compose up
```

### Standalone Docker Run

```bash
docker run \
    --env-file .env \
    -p 8123:8000 \
    -e REDIS_URI="redis://your-redis:6379" \
    -e DATABASE_URI="postgresql://user:pass@host:5432/db" \
    -e LANGSMITH_API_KEY="your-api-key" \
    my-langgraph-app
```

---

## Testing Your Application

### Unit Testing

#### Python (pytest)

```bash
uv add --dev pytest
```

```python
import pytest
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

def test_basic_agent_execution():
    checkpointer = MemorySaver()

    class MyState(TypedDict):
        my_key: str

    graph = StateGraph(MyState)
    graph.add_node("node1", lambda state: {"my_key": "hello"})
    graph.add_edge(START, "node1")
    graph.add_edge("node1", END)

    compiled_graph = graph.compile(checkpointer=checkpointer)
    result = compiled_graph.invoke(
        {"my_key": "initial"},
        config={"configurable": {"thread_id": "1"}}
    )

    assert result["my_key"] == "hello"
```

#### JavaScript (vitest)

```bash
npm install -D vitest
```

```typescript
import { test, expect } from 'vitest';
import { StateGraph, START, END, MemorySaver } from '@langchain/langgraph';
import { z } from "zod";

const State = z.object({
  my_key: z.string(),
});

test('basic agent execution', async () => {
  const graph = new StateGraph(State)
    .addNode('node1', () => ({ my_key: 'hello' }))
    .addEdge(START, 'node1')
    .addEdge('node1', END);

  const checkpointer = new MemorySaver();
  const compiled = graph.compile({ checkpointer });

  const result = await compiled.invoke(
    { my_key: 'initial' },
    { configurable: { thread_id: '1' } }
  );

  expect(result.my_key).toBe('hello');
});
```

### Testing Deployed API

To test a deployed LangGraph API server, you can use either the Python SDK or cURL.

> **Note**: The `langgraph-sdk` package is different from the `langgraph` package:
> - **`langgraph`**: Used for building and defining graphs locally
> - **`langgraph-sdk`**: A lightweight client library for interacting with deployed LangGraph API servers
>
> You only need `langgraph-sdk` when calling a remote/deployed LangGraph server. For local development and testing, use the `langgraph` package directly.

#### Using Python SDK

```bash
uv add langgraph-sdk
```

```python
from langgraph_sdk import get_sync_client

client = get_sync_client(
    url="your-deployment-url",
    api_key="your-langsmith-api-key"
)

for chunk in client.runs.stream(
    None,         # Threadless run
    "agent",      # Graph name from langgraph.json
    input={
        "messages": [{
            "role": "human",
            "content": "What is LangGraph?",
        }],
    },
    stream_mode="updates",
):
    print(f"Event: {chunk.event}")
    print(chunk.data)
```

#### Using cURL

```bash
curl -s --request POST \
    --url <DEPLOYMENT_URL>/runs/stream \
    --header 'Content-Type: application/json' \
    --header "X-Api-Key: <LANGSMITH_API_KEY>" \
    --data '{
        "assistant_id": "agent",
        "input": {
            "messages": [
                {
                    "role": "human",
                    "content": "What is LangGraph?"
                }
            ]
        },
        "stream_mode": "updates"
    }'
```

#### Understanding Stream Response Format

The streaming API returns Server-Sent Events (SSE). Each event consists of:
- **`event:`** - The event type
- **`data:`** - JSON payload
- **`id:`** - Unique event identifier

**Example Response:**

```
event: metadata
data: {"run_id":"019b5b5c-5c59-7452-8688-0adc55323fe7","attempt":1}
id: 1766764338976-0

event: updates
data: {"agent":{"messages":["Hello, world!","Hello from agent!"]}}
id: 1766764339042-0
```

**Stream Modes:**

| Mode | Description |
|------|-------------|
| `updates` | Returns state updates from each node as they complete |
| `values` | Returns the full state after each node execution |
| `messages` | Returns individual messages as they are generated (for chat applications) |
| `events` | Returns all internal events (most verbose) |

**Parsing SSE in Python:**

```python
import httpx

response = httpx.post(
    f"{deployment_url}/runs/stream",
    json={"assistant_id": "agent", "input": {...}, "stream_mode": "updates"},
    headers={"X-Api-Key": api_key},
)

for line in response.iter_lines():
    if line.startswith("data: "):
        import json
        data = json.loads(line[6:])
        print(data)
```

---

## LangGraph Platform Deployment

### Prerequisites

- GitHub account
- LangSmith account

### Deployment Steps

1. **Push your code to GitHub**

   Ensure your repository contains:
   - `langgraph.json` configuration
   - Your graph code
   - Dependency file (`requirements.txt` or `package.json`)

2. **Deploy via LangSmith UI**

   - Log in to [LangSmith](https://smith.langchain.com/)
   - Navigate to **Deployments** in the left sidebar
   - Click **+ New Deployment**
   - Connect your GitHub account if needed
   - Select your repository and click **Submit**

3. **Monitor Deployment**

   - Deployment typically takes up to 15 minutes
   - Monitor status in the **Deployment details** view

4. **Access Your Deployment**

   - Copy the **API URL** from deployment details
   - Use **LangGraph Studio** button to interact with your graph

### CLI Deployment

```bash
# Install CLI
uv add langgraph-cli

# Deploy
langgraph deploy --config langgraph.json
```

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `langgraph dev` | Start development server with hot reload |
| `langgraph build -t <tag>` | Build Docker image |
| `langgraph up` | Run server in Docker container |
| `langgraph dockerfile` | Generate Dockerfile |
| `langgraph deploy` | Deploy to LangGraph Platform |

---

## Resources

- [LangGraph Documentation](https://docs.langchain.com/langgraph-platform)
- [LangSmith](https://smith.langchain.com/)
- [LangGraph Studio](https://github.com/langchain-ai/langgraph-studio)
