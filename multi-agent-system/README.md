# Multi-Agent System

A minimal coordinator that routes each incoming task to the best specialist agent, with a full trace of who did what. Deterministic — the goal is the orchestration pattern, not the intelligence of any single agent.

## Agents

- **Calculator** — extracts arithmetic (digits or number words) and evaluates in a sandboxed `eval`
- **Summarizer** — picks the first, longest-middle, and last sentence
- **Retrieval** — bag-of-words scoring over a tiny in-memory knowledge base

## Coordinator

Each agent implements `can_handle(task) -> float` (a confidence score). The coordinator picks the highest and delegates. Every step (route decision, agent action, intermediate result) is logged to a `Trace` shown alongside the answer.

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Layout

- `app.py` — Streamlit UI
- `agents.py` — Agent base class, three specialists, Coordinator

## Extending

Swap `CalculatorAgent`/`RetrievalAgent` for LangChain/CrewAI-backed agents and the coordinator keeps working. The routing contract (`can_handle` + `run`) is what matters.
