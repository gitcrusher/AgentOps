from typing import TypedDict, List
import operator
from typing import Annotated

class AgentState(TypedDict):
    raw_input: str
    sub_tasks: List[dict]
    knowledge_results: Annotated[List[dict], operator.add]
    action_results: Annotated[List[dict], operator.add]
    escalations: Annotated[List[dict], operator.add]
    trace: Annotated[List[dict], operator.add]
    final_answer: str
