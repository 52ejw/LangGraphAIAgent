# Research Assistant Agent (LangGraph)

A LangGraph-based agent that plans a research task, calls tools to
gather information, and synthesizes a sourced answer — with state
persisted across conversation turns.

## Setup

1. Create a virtual environment and install dependencies:

```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
```

2. (Optional) To use real Claude synthesis instead of the built-in
   mock LLM, set an API key:

```bash
   export ANTHROPIC_API_KEY=sk-ant-...
```

Without this, the agent runs fully offline using a deterministic
`MockLLM`, so it works out of the box for grading/demo purposes.

## Run

```bash
python main.py
```

Type a research question, e.g.:
