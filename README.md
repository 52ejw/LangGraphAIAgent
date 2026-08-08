# Research Assistant Agent (LangGraph)

This project implements a research assistant agent using LangGraph. The agent takes a research question from the user, creates a research plan, gathers information using different tools, and generates a final answer with sources.

The workflow is divided into several nodes:

- Planner Node: Creates smaller research steps based on the user's question
- Researcher Node: Selects and calls available research tools
- Responder Node: Combines the collected information and generates the final response
- Error Handler Node: Handles failures and returns a user-friendly message

The agent also uses LangGraph state management with MemorySaver to maintain conversation history, allowing it to handle follow-up questions across multiple interactions.

## Features

- Accepts research topics or questions from users
- Generates a multi-step research plan
- Uses multiple tools:
  - Web search simulation
  - Document retrieval
- Maintains conversation state between turns
- Supports follow-up questions using previous context
- Provides sources used during the research process
- Includes basic error handling for failed operations
- Supports both MockLLM and real Claude API usage

## Project Structure

LangGraphAIAgent/
│
├── src/
│ ├── main.py # Runs the application and handles user interaction
│ ├── graph.py # Defines the LangGraph workflow and node connections
│ ├── nodes.py # Contains planner, researcher, responder, and error nodes
│ ├── state.py # Defines the shared agent state
│ ├── tools.py # Contains the research tools
│ └── llm.py # Handles LLM calls and MockLLM fallback
│
├── requirements.txt
├── README.md
└── .env


## Setup

### 1. Create a virtual environment

```bash
python -m venv venv
```

Activate the virtual environment:

**Mac/Linux:**

```bash
source venv/bin/activate
```

**Windows:**

```bash
venv\Scripts\activate
```

### 2. Install dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 3. Configure Claude API (Optional)

By default, the agent uses a built-in MockLLM, allowing it to run without an external API.

To use real Claude synthesis, create a `.env` file in the project directory and add: ANTHROPIC_API_KEY=your_api_key_here

When the API key is available, the agent will automatically use Claude instead of the MockLLM.

> **Note:** A `.gitignore` is included to keep `.env`, `venv/`, `__pycache__/`, and other local files out of version control, so your API key won't be accidentally committed.

## Run

Run the application using:

```bash
python src/main.py
```
