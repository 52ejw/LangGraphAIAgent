from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from state import AgentState
from nodes import planner_node, researcher_node, responder_node, handle_error_node


def route_after_planner(state: AgentState) -> str:
    return "error" if state["next_action"] == "error" else "research"


def route_after_research(state: AgentState) -> str:
    return "research" if state["next_action"] == "research" else "respond"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("responder", responder_node)
    graph.add_node("handle_error", handle_error_node)

    graph.add_edge(START, "planner")

    graph.add_conditional_edges(
        "planner",
        route_after_planner,
        {"research": "researcher", "error": "handle_error"},
    )

    graph.add_conditional_edges(
        "researcher",
        route_after_research,
        {"research": "researcher", "respond": "responder"},
    )

    graph.add_edge("responder", END)
    graph.add_edge("handle_error", END)

    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer)