from typing import Annotated, Dict, List, Optional, TypedDict

# Allows LangGraph to add new messages/results to existing lists
# instead of replacing the whole list 
import operator

# Describes the information stored for each source
class Source(TypedDict):
    title: str
    url: str
    snippet: str

# Describes the information stored for each research result
class ResearchResult(TypedDict):
    step: str
    tool: str
    content: str

# All the information the research agent needs while it is working on a question 
class AgentState(TypedDict):
    # Stores conversation messages
    messages: Annotated[List[Dict[str, str]], operator.add]

    # Current research topic 
    topic: str
    # List of research questions created by MockLLM
    plan: List[str]
    # Keep track of which research question is being handled 
    current_step: int

    # Stores results collected from the research tools 
    research_results: Annotated[List[ResearchResult], operator.add]
    # Stores source found during research 
    sources: Annotated[List[Source], operator.add]

    # Tells the workflow what's next
    next_action: str

    # Stores error message if something goes wrong 
    error: Optional[str]

    # Stores final answer shown to the user 
    final_answer: Optional[str]