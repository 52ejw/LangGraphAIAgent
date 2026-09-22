from typing import Any, Dict

# Store agent state 
from state import AgentState

# Research tools and the function that chooses which tool to use
from tools import TOOL_REGISTRY, choose_tool

# Mock LLM for planning and summarising
from llm import generate_plan, synthesize_answer


# Get user's recent message
def get_latest_user_message(state: AgentState) -> str:

    # Reverse chronological order to find the most recent message
    for message in reversed(state["messages"]):
        if message.get("role") == "user":
            return message["content"]

    # Empty string if no user message is found
    return ""

# Resolve topic for the current question
def resolve_topic(state: AgentState) -> str:

    latest_message = get_latest_user_message(state)

    # Gets all previous user messages 
    user_messages = [
        message["content"]
        for message in state["messages"]
        if message.get("role") == "user"
    ]

    # Refers to previous question if current question refers back to it
    previous_topic = user_messages[-2] if len(user_messages) >= 2 else ""

    reference_words = {
        "it",
        "its",
        "they",
        "their",
        "this",
        "that",
    }

    words = latest_message.lower().split()

    # Links new question to previous topic
    if previous_topic and any(word in words for word in reference_words):
        return f"{latest_message} (related to {previous_topic})"

    return latest_message

# Create research plan
def planner_node(state: AgentState) -> Dict[str, Any]:

    topic = resolve_topic(state)

    # Stop if user did not provide a topic 
    if not topic:
        return {
            "error": "No research topic was provided.",
            "next_action": "error",
        }

    try:
        # MockLLM creates the research steps
        plan = generate_plan(topic)
    except Exception as exc:
        # Sends error to error handling
        return {
            "error": f"Planning failed: {exc}",
            "next_action": "error",
        }

    # Stop if no reseach steps created 
    if not plan:
        return {
            "error": "Could not generate a research plan for this topic.",
            "next_action": "error",
        }

    # Saves plan and prepares agent for research
    return {
        "topic": topic,
        "plan": plan,
        "current_step": 0,

        "research_results": [],
        "sources": [],

        "next_action": "research",

        "messages": [
            {
                "role": "system",
                "content": f"Research plan created with {len(plan)} steps: {plan}",
            }
        ],
    }


# Performs one research step
def researcher_node(state: AgentState) -> Dict[str, Any]:

    plan = state["plan"]
    step_index = state["current_step"]

    # Create final answer if all research steps finished
    if step_index >= len(plan):
        return {
            "next_action": "respond"
        }

    # Get current research question
    research_step = plan[step_index]

    # Choose most suitable tool 
    tool_name = choose_tool(research_step)
    tool_function = TOOL_REGISTRY.get(tool_name)

    # Stop if selected tool does not exist 
    if tool_function is None:
        return {
            "error": f"Research tool '{tool_name}' is not available.",
            "next_action": "error",
        }

    try:
        # Run the selected tool 
        result = tool_function(research_step)

        content = result["content"]
        sources = result.get("sources", [])

    except Exception as exc:
        # Keep the workflow running even if a research tool fails
        content = f"[Tool error] {tool_name} failed: {exc}"
        sources = []

    # Move to the next research step
    next_step = step_index + 1

    # Check if there's more steps to complete
    if next_step < len(plan):
        next_action = "research"
    else:
        next_action = "respond"

    # Saves research result 
    return {
        "research_results": [
            {
                "step": research_step,
                "tool": tool_name,
                "content": content,
            }
        ],
        "sources": sources,
        "current_step": next_step,
        "next_action": next_action,
    }

# Creates final response using research findings
def responder_node(state: AgentState) -> Dict[str, Any]:
    # Combines all research results into a single text
    findings = "\n".join(
        f"- ({result['tool']}) {result['step']}: {result['content']}"
        for result in state["research_results"]
    )

    try:
        # MockLLM turns research findings into a summary \
        answer = synthesize_answer(state["topic"], findings)
    except Exception as exc:
        # If summarising fails, show research instead
        answer = (
            "I gathered the research successfully, but I could not "
            f"generate the final summary because of an error: {exc}\n\n"
            f"Raw findings:\n{findings}"
        )

    # Formats sources to be shown below the answer 
    source_lines = "\n".join(
        f"  [{index}] {source['title']} - {source['url']}"
        for index, source in enumerate(state.get("sources", []), start=1)
    )

    # Add sources
    if source_lines:
        answer = f"{answer}\n\nSources:\n{source_lines}"

    # Saves final answer and add to conversation
    return {
        "final_answer": answer,
        "messages": [
            {
                "role": "assistant",
                "content": answer,
            }
        ],
        "next_action": "done",
    }

# Error handling
def handle_error_node(state: AgentState) -> Dict[str, Any]:

    error_message = state.get("error") or "An unknown error occurred."

    response = (
        "I ran into a problem while researching this topic: "
        f"{error_message}\n"
        "Please try rephrasing your question or providing more detail."
    )

    return {
        "final_answer": response,
        "messages": [
            {
                "role": "assistant",
                "content": response,
            }
        ],
        "next_action": "done",
    }