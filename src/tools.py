from typing import Dict, Any, List
import random

_WEB_INDEX = {
    "langgraph": [
        {
            "title": "LangGraph: Building Stateful Multi-Actor Applications",
            "url": "https://example.com/langgraph-overview",
            "snippet": "LangGraph models agent workflows as graphs of nodes and "
                       "edges, allowing explicit control over state and branching.",
        },
        {
            "title": "Conditional Edges in LangGraph",
            "url": "https://example.com/langgraph-conditional-edges",
            "snippet": "Conditional edges let a graph route to different nodes "
                       "based on the current state, enabling agent-like decisions.",
        },
    ],
    "climate": [
        {
            "title": "Global Climate Trends 2025 Report",
            "url": "https://example.com/climate-2025",
            "snippet": "Average global temperatures rose again in 2025, driven "
                       "by continued greenhouse gas emissions.",
        },
    ],
    "default": [
        {
            "title": "General Overview Article",
            "url": "https://example.com/general-overview",
            "snippet": "A broad summary covering background and recent context "
                       "on the requested topic.",
        },
    ],
}

_DOC_KB = {
    "langgraph": [
        {
            "title": "Internal Doc: Agent Architecture Guidelines",
            "url": "kb://internal/agent-architecture",
            "snippet": "Our internal standard recommends separating planning, "
                       "tool execution, and response synthesis into distinct nodes.",
        }
    ],
    "default": [
        {
            "title": "Internal Doc: Research Methodology Notes",
            "url": "kb://internal/research-methodology",
            "snippet": "Internal notes on how to structure multi-step research "
                       "for open-ended topics.",
        }
    ],
}


def _match_key(query: str, index: Dict[str, Any]) -> str:
    q = query.lower()
    for key in index:
        if key != "default" and key in q:
            return key
    return "default"


def web_search_simulation(query: str) -> Dict[str, Any]:
    if not query or not query.strip():
        raise ValueError("Empty query passed to web_search_simulation")

    key = _match_key(query, _WEB_INDEX)
    results = _WEB_INDEX[key]

    content = " ".join(r["snippet"] for r in results)
    return {"content": f"[Web search] {content}", "sources": results}


def document_retrieval(query: str) -> Dict[str, Any]:
    if not query or not query.strip():
        raise ValueError("Empty query passed to document_retrieval")

    key = _match_key(query, _DOC_KB)
    results = _DOC_KB[key]

    content = " ".join(r["snippet"] for r in results)
    return {"content": f"[Document retrieval] {content}", "sources": results}


TOOL_REGISTRY = {
    "web_search_simulation": web_search_simulation,
    "document_retrieval": document_retrieval,
}


def choose_tool(step: str) -> str:
    step_lower = step.lower()
    news_words = ("recent", "latest", "current", "news", "trend", "2025", "2026")
    if any(w in step_lower for w in news_words):
        return "web_search_simulation"
    if "internal" in step_lower or "guideline" in step_lower or "policy" in step_lower:
        return "document_retrieval"
    return random.choice(["web_search_simulation", "document_retrieval"])