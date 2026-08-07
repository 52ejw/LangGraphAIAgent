from typing import Dict, Any
from state import AgentState
from tools import TOOL_REGISTRY, choose_tool
from llm import generate_plan, synthesize_answer


def extract_latest_user_message(state: AgentState) -> str:
    for msg in reversed(state["messages"]):
        if msg.get("role") == "user":
            return msg["content"]
    return ""

#Planner
def planner_node(state: AgentState) -> Dict[str, Any]:
    topic = state.get("topic") or extract_latest_user_message(state)

    try:
        plan = generate_plan(topic)
    except Exception as e:
        return {
            "error": f"Planning failed: {e}",
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
            {"role": "system", "content": f"Plan created ({len(plan)} steps): {plan}"}
        ],
    }

#Researcher
def researcher_node(state: AgentState) -> Dict[str, Any]:
    plan = state["plan"]
    step_idx = state["current_step"]

    if step_idx >= len(plan):
        return {"next_action": "respond"}

    step = plan[step_idx]
    tool_name = choose_tool(step)
    tool_fn = TOOL_REGISTRY[tool_name]

    try:
        result = tool_fn(step)
        content = result["content"]
        sources = result.get("sources", [])
    except Exception as e:
        content = f"[Tool error] '{tool_name}' failed for step '{step}': {e}"
        sources = []

    new_step = step_idx + 1
    next_action = "research" if new_step < len(plan) else "respond"

    return {
        "research_results": [{"step": step, "tool": tool_name, "content": content}],
        "sources": sources,
        "current_step": new_step,
        "next_action": next_action,
    }

#Responder
def responder_node(state: AgentState) -> Dict[str, Any]:
    findings_text = "\n".join(
        f"- ({r['tool']}) {r['step']}: {r['content']}" for r in state["research_results"]
    )

    try:
        answer = synthesize_answer(state["topic"], findings_text)
    except Exception as e:
        answer = (
            f"I gathered research but couldn't synthesize a final answer due to "
            f"an error ({e}). Here are the raw findings:\n{findings_text}"
        )

    source_lines = "\n".join(
        f"  [{i+1}] {s['title']} - {s['url']}" for i, s in enumerate(state["sources"])
    )
    full_answer = f"{answer}\n\nSources:\n{source_lines}" if source_lines else answer

    return {
        "final_answer": full_answer,
        "messages": [{"role": "assistant", "content": full_answer}],
        "next_action": "done",
    }

#Error Handling 
def handle_error_node(state: AgentState) -> Dict[str, Any]:
    error_msg = state.get("error", "An unknown error occurred.")
    apology = (
        f"I ran into a problem while researching this topic: {error_msg} "
        "Could you rephrase your question or provide a bit more detail?"
    )
    return {
        "final_answer": apology,
        "messages": [{"role": "assistant", "content": apology}],
    }