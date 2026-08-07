from typing import Any, Dict

from state import AgentState
from tools import TOOL_REGISTRY, choose_tool
from llm import generate_plan, synthesize_answer


def get_latest_user_message(state: AgentState) -> str:

    for message in reversed(state["messages"]):
        if message.get("role") == "user":
            return message["content"]

    return ""


def resolve_topic(state: AgentState) -> str:

    latest_message = get_latest_user_message(state)

    user_messages = [
        message["content"]
        for message in state["messages"]
        if message.get("role") == "user"
    ]

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

    if previous_topic and any(word in words for word in reference_words):
        return f"{latest_message} (related to {previous_topic})"

    return latest_message


def planner_node(state: AgentState) -> Dict[str, Any]:

    topic = resolve_topic(state)

    if not topic:
        return {
            "error": "No research topic was provided.",
            "next_action": "error",
        }

    try:
        plan = generate_plan(topic)
    except Exception as exc:
        return {
            "error": f"Planning failed: {exc}",
            "next_action": "error",
        }

    if not plan:
        return {
            "error": "Could not generate a research plan for this topic.",
            "next_action": "error",
        }

    return {
        "topic": topic,
        "plan": plan,
        "current_step": 0,
        "next_action": "research",
        "messages": [
            {
                "role": "system",
                "content": f"Research plan created with {len(plan)} steps: {plan}",
            }
        ],
    }


def researcher_node(state: AgentState) -> Dict[str, Any]:

    plan = state["plan"]
    step_index = state["current_step"]

    if step_index >= len(plan):
        return {"next_action": "respond"}

    research_step = plan[step_index]
    tool_name = choose_tool(research_step)
    tool_function = TOOL_REGISTRY.get(tool_name)

    if tool_function is None:
        return {
            "error": f"Research tool '{tool_name}' is not available.",
            "next_action": "error",
        }

    try:
        result = tool_function(research_step)
    except Exception as exc:
        result = {
            "content": f"[Tool error] {tool_name} failed: {exc}",
            "sources": [],
        }

    next_step = step_index + 1

    if next_step < len(plan):
        next_action = "research"
    else:
        next_action = "respond"

    return {
        "research_results": [
            {
                "step": research_step,
                "tool": tool_name,
                "content": result["content"],
            }
        ],
        "sources": result.get("sources", []),
        "current_step": next_step,
        "next_action": next_action,
    }


def responder_node(state: AgentState) -> Dict[str, Any]:

    findings = "\n".join(
        f"- ({result['tool']}) {result['step']}: {result['content']}"
        for result in state["research_results"]
    )

    try:
        answer = synthesize_answer(state["topic"], findings)
    except Exception as exc:
        answer = (
            "I gathered the research successfully, but I could not "
            f"generate the final summary because of an error: {exc}\n\n"
            f"Raw findings:\n{findings}"
        )

    sources = "\n".join(
        f"[{index}] {source['title']} - {source['url']}"
        for index, source in enumerate(state["sources"], start=1)
    )

    if sources:
        answer = f"{answer}\n\nSources:\n{sources}"

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