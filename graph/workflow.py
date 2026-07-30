from langgraph.graph import StateGraph, START, END
from graph.state import AgentState
from agents.router_agent import get_router_completion
from agents.knowledge_agent import get_knowledge_answer
from agents.action_agent import get_action_result
from agents.escalation_agent import escalate
import json
import uuid
import os

def router_node(state: AgentState):
    query = state["raw_input"]
    res = get_router_completion(query)
    trace_item = {"agent": "Router", "output": res}
    return {"sub_tasks": res.get("sub_tasks", []), "trace": [trace_item]}

def knowledge_node(state: AgentState):
    results = []
    traces = []
    for task in state.get("sub_tasks", []):
        if task.get("type") == "knowledge_query":
            ans = get_knowledge_answer(task["text"])
            ans["_task_text"] = task["text"]
            results.append(ans)
            traces.append({"agent": "Knowledge Agent", "output": ans["answer"], "confidence": ans["confidence"]})
    return {"knowledge_results": results, "trace": traces}

def action_node(state: AgentState):
    results = []
    traces = []
    for task in state.get("sub_tasks", []):
        if task.get("type") == "action_request":
            ans = get_action_result(task["text"])
            ans["_task_text"] = task["text"]
            results.append(ans)
            traces.append({"agent": "Action Agent", "output": ans.get("result") or ans.get("reason"), "success": ans["success"]})
    return {"action_results": results, "trace": traces}

def escalation_node(state: AgentState):
    esc = escalate(state.get("knowledge_results", []), state.get("action_results", []), state.get("trace", []))
    traces = []
    if esc:
        for e in esc:
            traces.append({"agent": "Escalation Agent", "output": {"status": "needs_human_review", "reason": e["reason"]}})
    else:
        traces.append({"agent": "Escalation Agent", "output": {"status": "resolved"}})
    return {"escalations": esc, "trace": traces}

def merger_node(state: AgentState):
    parts = []
    
    for kr in state.get("knowledge_results", []):
        if kr.get("confidence", 0.0) >= 0.55:
            parts.append(kr["answer"])
            
    for ar in state.get("action_results", []):
        if ar.get("success"):
            parts.append(f"Successfully processed action: {ar.get('tool_called')} (Result: {ar.get('result')})")
            
    for e in state.get("escalations", []):
        parts.append(f"I wasn't confident enough in an answer to this part of your request, so I've flagged it for a team member to review instead of guessing. [{e['reason']}]")
        
    if not parts:
        final_answer = "I'm here to help with IT policies, hardware requests, or ticket management. How can I assist you today?"
    else:
        final_answer = "\n\n".join(parts)
        
    os.makedirs("logs", exist_ok=True)
    session_id = str(uuid.uuid4())
    with open(f"logs/trace_{session_id}.jsonl", "w") as f:
        f.write(json.dumps({"final_answer": final_answer, "trace": state.get("trace", [])}) + "\n")
        
    return {"final_answer": final_answer}

def route_after_router(state: AgentState):
    intents = [t.get("type") for t in state.get("sub_tasks", [])]
    destinations = []
    if "knowledge_query" in intents:
        destinations.append("knowledge_node")
    if "action_request" in intents:
        destinations.append("action_node")
    
    if not destinations: 
        return "merger_node"
    return destinations

workflow = StateGraph(AgentState)
workflow.add_node("router_node", router_node)
workflow.add_node("knowledge_node", knowledge_node)
workflow.add_node("action_node", action_node)
workflow.add_node("escalation_node", escalation_node)
workflow.add_node("merger_node", merger_node)

workflow.add_edge(START, "router_node")
workflow.add_conditional_edges("router_node", route_after_router, ["knowledge_node", "action_node", "merger_node"])
workflow.add_edge("knowledge_node", "escalation_node")
workflow.add_edge("action_node", "escalation_node")
workflow.add_edge("escalation_node", "merger_node")
workflow.add_edge("merger_node", END)

graph = workflow.compile()
