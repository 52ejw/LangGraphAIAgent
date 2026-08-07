from typing import TypedDict, List, Dict, Any, Optional, Annotated
import operator


class Source(TypedDict):
    title: str
    url: str
    snippet: str


class ResearchResult(TypedDict):
    step: str
    tool: str
    content: str


class AgentState(TypedDict):
    messages: Annotated[List[Dict[str, str]], operator.add]

    topic: str

    plan: List[str]

    current_step: int

    research_results: Annotated[List[ResearchResult], operator.add]
    sources: Annotated[List[Source], operator.add]

    next_action: str  

    error: Optional[str]

    final_answer: Optional[str]