from typing import Any, Dict
import random

# Mock web sources
WEB_INDEX = {
    "langgraph": [
        {
            "title": "LangGraph Documentation",
            "url": "https://docs.langchain.com/oss/python/langgraph/overview",
            "snippet": (
                "LangGraph is a framework for building stateful, "
                "multi-step applications with language models."
            ),
        },
        {
            "title": "LangGraph Graph Concepts",
            "url": "https://docs.langchain.com/oss/python/langgraph/graph-api",
            "snippet": (
                "LangGraph represents workflows using nodes, edges, "
                "state, and conditional routing."
            ),
        },
    ],
    "climate": [
        {
            "title": "Global Climate Trends",
            "url": "https://example.com/climate-trends",
            "snippet": (
                "A simulated source containing background information "
                "about global climate trends."
            ),
        },
    ],
    "default": [
        {
            "title": "General Research Overview",
            "url": "https://example.com/general-overview",
            "snippet": (
                "A simulated research source containing general "
                "background information about the requested topic."
            ),
        },
    ],
}


# Mock documents
DOCUMENT_INDEX = {
    "langgraph": [
        {
            "title": "Internal Agent Architecture Guidelines",
            "url": "kb://internal/agent-architecture",
            "snippet": (
                "The recommended architecture separates planning, "
                "tool execution, and response synthesis into different nodes."
            ),
        }
    ],
    "default": [
        {
            "title": "Internal Research Methodology Notes",
            "url": "kb://internal/research-methodology",
            "snippet": (
                "Internal notes describing how to structure "
                "multi-step research for open-ended topics."
            ),
        }
    ],
}


# Looks for a known topic inside the user's research question
def find_matching_topic(query: str, index: Dict[str, Any]) -> str:
  
    query_lower = query.lower()

    # Check each topic except "default"
    for key in index:
        if key != "default" and key in query_lower:
            return key

    # Use general results when no specific topic found 
    return "default"


# Web search simulation
def web_search_simulation(query: str) -> Dict[str, Any]:

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    # Find most relevant topic
    topic_key = find_matching_topic(query, WEB_INDEX)
    results = WEB_INDEX[topic_key]

    # Combine information from sources
    content = " ".join(result["snippet"] for result in results)

    return {
        "content": f"[Web search] {content}",
        "sources": results,
    }


# Internal document search simulation
def document_retrieval(query: str) -> Dict[str, Any]:

    if not query or not query.strip():
        raise ValueError("Document search query cannot be empty.")

    # Find most relevant topic
    topic_key = find_matching_topic(query, DOCUMENT_INDEX)
    results = DOCUMENT_INDEX[topic_key]

    # Combine information from documents
    content = " ".join(result["snippet"] for result in results)

    return {
        "content": f"[Document retrieval] {content}",
        "sources": results,
    }


# Available research tools.
TOOL_REGISTRY = {
    "web_search_simulation": web_search_simulation,
    "document_retrieval": document_retrieval,
}


# Decides which research tool should be used for a research question
def choose_tool(research_step: str) -> str:

    step = research_step.lower()

    recent_keywords = (
        "recent",
        "latest",
        "current",
        "news",
        "trend",
        "2025",
        "2026",
    )

    internal_keywords = (
        "internal",
        "guideline",
        "policy",
    )

    # Web search for recent topics 
    if any(word in step for word in recent_keywords):
        return "web_search_simulation"

    # Document search for internal topics 
    if any(word in step for word in internal_keywords):
        return "document_retrieval"

    # Web search for other questions
    return "web_search_simulation"