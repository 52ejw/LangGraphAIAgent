# Tools needed to build workflow
from langgraph.graph import StateGraph, START, END

# Save conversation state while program is running 
from langgraph.checkpoint.memory import MemorySaver

# Import structure used to store agent information 
from state import AgentState

# Import functions that each step of the workflow will run
from nodes import planner_node, researcher_node, responder_node, handle_error_node


def route_after_planner(state: AgentState) -> str:
    # If planning fails, go to error hanldling, otherwise go to research
    return "error" if state["next_action"] == "error" else "research"


def route_after_research(state: AgentState) -> str:
    # Continue research if there is more research, otherwise move to final response
    return "research" if state["next_action"] == "research" else "respond"


def build_graph():
    graph = StateGraph(AgentState)

    # Add each part of the research assistant as a separate step
    graph.add_node("planner", planner_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("responder", responder_node)
    graph.add_node("handle_error", handle_error_node)

    # Wrokflow start by creating research plan
    graph.add_edge(START, "planner")

    # Choose between research or error handling after planning
    graph.add_conditional_edges(
        "planner",
        route_after_planner,
        {"research": "researcher", "error": "handle_error"},
    )

    # Do more research or create final answer
    graph.add_conditional_edges(
        "researcher",
        route_after_research,
        {"research": "researcher", "respond": "responder"},
    )

    #Workflow ends after final response or error handling
    graph.add_edge("responder", END)
    graph.add_edge("handle_error", END)

    # Keeps conversation state in memory
    checkpointer = MemorySaver()
    # Builds final runnable version of the workflow
    return graph.compile(checkpointer=checkpointer)