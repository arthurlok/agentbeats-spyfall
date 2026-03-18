# Spyfall Green Agent

A green agent that orchestrates games of [Spyfall](https://en.wikipedia.org/wiki/Spyfall_(card_game)) on [AgentBeats](https://agentbeats.dev). It manages the full game lifecycle — assigning roles, running question rounds, and scoring the outcome — then reports results back to the platform.

View the leaderboard: [agentbeats-spyfall-leaderboard](../agentbeats-spyfall-leaderboard)

## How It Works

At the start of each game:
- One player is secretly assigned as the **spy**, the rest are **non-spies**
- Non-spies know the secret location; the spy does not
- The location is chosen randomly (or specified via config) from 27 possible locations

Each round, players take turns asking questions. The spy tries to blend in and deduce the location; non-spies try to expose the spy without revealing the location outright.

The game ends in one of two ways:
- **Spy guess**: The spy names the location on their turn — instant win if correct, instant loss if wrong
- **Vote**: After all rounds, non-spies vote on who they think the spy is — majority wins

### Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `location` | Secret location, or `"Random"` to pick one | `"Random"` |
| `num_rounds` | Number of action rounds before voting | `3` |

Supports **3–8 players**.

## Project Structure

```
src/
├─ main.py           # Entrypoint — selects green or white role via ROLE env var
├─ green/
│  ├─ agent.py       # Green agent: validates requests, runs games, formats results
│  ├─ game_env.py    # SpyfallEnv: full game loop, prompts, voting logic
│  ├─ executor.py    # A2A task executor
│  ├─ messenger.py   # A2A messaging utilities
│  └─ server.py      # A2A server setup and agent card
└─ white/
   ├─ player.py      # LLM-powered player using OpenRouter (Gemini 2.0 Flash by default)
   ├─ agent.py       # White agent wrapper
   ├─ executor.py    # A2A task executor
   └─ server.py      # A2A server setup and agent card
tests/
└─ test_agent.py     # Agent conformance tests
Dockerfile           # Docker configuration
pyproject.toml       # Python dependencies
```

This repo serves a dual purpose: the **green** role runs as the game orchestrator (submitted to AgentBeats), and the **white** role is a bundled baseline purple agent for local testing.

## Running Locally

Set the `ROLE` environment variable to `green` or `white`, and provide your `OPENROUTER_API_KEY`.

```bash
# Install dependencies
uv sync

# Run the green agent (orchestrator)
ROLE=green uv run -m src.main

# Run a white agent (player) on a different port
ROLE=white uv run -m src.main --port 9010
```

## Running with Docker

```bash
# Build the image
docker build -t spyfall-agent .

# Run as green agent
docker run -p 9009:9009 -e ROLE=green -e OPENROUTER_API_KEY=<key> spyfall-agent

# Run as white agent
docker run -p 9010:9009 -e ROLE=white -e OPENROUTER_API_KEY=<key> spyfall-agent
```

## Testing

```bash
# Install test dependencies
uv sync --extra test

# Start the green agent
ROLE=green uv run -m src.main

# Run A2A conformance tests
uv run pytest --agent-url http://localhost:9009
```

## Publishing

The CI workflow (`.github/workflows/test-and-publish.yml`) automatically builds, tests, and publishes a Docker image to GitHub Container Registry on each push.

Add `OPENROUTER_API_KEY` to your repository secrets (Settings → Secrets and variables → Actions).

- **Push to `main`** → publishes `latest`:
```
ghcr.io/<your-username>/agentbeats-spyfall-green-agent:latest
```

- **Create a git tag** (e.g. `git tag v1.0.0 && git push origin v1.0.0`) → publishes version tags:
```
ghcr.io/<your-username>/agentbeats-spyfall-green-agent:1.0.0
ghcr.io/<your-username>/agentbeats-spyfall-green-agent:1
```

> **Note:** Version tags must follow [semantic versioning](https://semver.org/) (e.g., `v1.0.0`).
