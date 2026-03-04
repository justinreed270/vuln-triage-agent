# agent/planner.py
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

def planner(state: dict) -> dict:
    """Node: LLM decides which tool to call next based on current state."""
    llm = ChatOllama(model="llama3.1:8b", base_url="http://localhost:11434")
    
    # Tell the LLM what's been done and what tools are available
    system_prompt = """You are a vulnerability triage agent controller. 
Based on the current state of work, decide what to do next.
You must respond with ONLY one of these exact strings:
- run_nmap
- lookup_cves
- write_report
- done

Rules:
- If no scan has been run yet, respond: run_nmap
- If scan results exist but no CVE lookup has been done, respond: lookup_cves  
- If both scan and CVE data exist but no report has been written, respond: write_report
- If a report exists, respond: done"""

    state_summary = f"""
Target: {state['target']}
Scan completed: {'Yes' if state.get('scan_results') else 'No'}
CVE lookup completed: {'Yes' if state.get('cve_results') else 'No'}
Report written: {'Yes' if state.get('report') else 'No'}
"""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Current state:\n{state_summary}\nWhat should be done next?")
    ])
    
    # Parse the LLM's decision — strip whitespace and lowercase for safety
    decision = response.content.strip().lower()
    
    # Validate — fallback if LLM goes off-script
    valid_actions = ["run_nmap", "lookup_cves", "write_report", "done"]
    if decision not in valid_actions:
        # Infer from state as fallback
        if not state.get("scan_results"):
            decision = "run_nmap"
        elif not state.get("cve_results"):
            decision = "lookup_cves"
        elif not state.get("report"):
            decision = "write_report"
        else:
            decision = "done"
    
    messages = state.get("messages", [])
    messages.append(f"[PLANNER] Next action: {decision}")
    return {"next_action": decision, "messages": messages}