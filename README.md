# Agentic AI Assistant

A production-ready LangChain application that uses Groq `openai/gpt-oss-120b`,
LangChain `create_agent`, tool selection, conversational memory, and FastAPI.

## Capabilities

- Uses LangChain v1 `create_agent`.
- Uses Groq as the LLM provider.
- Routes questions to Google Search, Wikipedia, arXiv, or a combination of tools.
- Maintains conversation memory by `conversation_id`.
- Exposes `/chat`, `/reset-memory`, `/health`, `/tools`, and `/config`.
- Keeps credentials in environment variables.
- Includes structured logging, typed schemas, deployment files, and tests.

## Project Structure

```text
app/
  main.py                 FastAPI app, middleware, exception handlers
  api/                    Routes and dependency providers
  agent/                  Agent builder, memory, prompt
  config/                 Settings, logging, Groq LLM factory
  schemas/                Pydantic request/response models
  services/               Use-case orchestration
  tools/                  Google, Wikipedia, arXiv tools and registry
  utils/                  Exceptions and helpers
tests/                    Unit and integration test examples
```

## Environment

Copy `.env.example` to `.env` and fill in the keys:

```bash
GROQ_API_KEY=...
GOOGLE_API_KEY=...
GOOGLE_CSE_ID=...
MODEL_NAME=openai/gpt-oss-120b
```

`GROQ_API_KEY` is required for `/chat`. `GOOGLE_API_KEY` and `GOOGLE_CSE_ID`
are required only when the agent chooses Google Search. Wikipedia and arXiv do
not require API keys.

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Run With Docker

```bash
docker compose up --build
```

## API Examples

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"conversation_id":"demo","message":"What happened in AI this week?"}'
```

```bash
curl -X POST http://localhost:8000/reset-memory \
  -H "Content-Type: application/json" \
  -d '{"conversation_id":"demo"}'
```

## Testing

```bash
pytest
ruff check .
```

## Adding A New Tool

1. Create `app/tools/new_tool.py`.
2. Implement `AssistantTool.as_langchain_tool`.
3. Add it to `ToolRegistry`.
4. Write a focused test.

The agent will decide when to use it from the tool name, schema, and
description, so new tools do not require route or service changes.

## Production Notes

- Replace `InMemorySaver` with a persistent LangGraph checkpointer for
  multi-instance deployments.
- Enable LangSmith tracing with `LANGSMITH_TRACING=true` and a valid API key.
- Put the API behind a gateway with authentication and request rate limits.
- Consider Redis caching for repeated web/research lookups.
