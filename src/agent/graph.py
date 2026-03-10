# agent/graph.py
from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.planner import planner
from agent.tools import run_nmap, lookup_cves, write_report

def route_next_action(state: dict) -> str:
    """Conditional edge function — reads next_action and routes to the right node."""
    action = state.get("next_action", "done")
    if action == "run_nmap":
        return "nmap"
    elif action == "lookup_cves":
        return "cve_lookup"
    elif action == "write_report":
        return "report"
    else:
        return END

def build_graph():
    graph = StateGraph(AgentState)
    
    # Add all nodes
    graph.add_node("planner", planner)
    graph.add_node("nmap", run_nmap)
    graph.add_node("cve_lookup", lookup_cves)
    graph.add_node("report", write_report)
    
    # Entry point — always start with the planner
    graph.set_entry_point("planner")
    
    # Conditional edge from planner — routes based on next_action
    graph.add_conditional_edges("planner", route_next_action)
    
    # After each tool runs, go BACK to the planner to decide what's next
    graph.add_edge("nmap", "planner")
    graph.add_edge("cve_lookup", "planner")
    graph.add_edge("report", "planner")
    
    return graph.compile()