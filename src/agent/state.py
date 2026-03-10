# agent/state.py
from typing import TypedDict, List, Optional

class AgentState(TypedDict):
    target: str                    # IP or hostname given by user
    scan_results: Optional[str]    # Raw nmap output
    cve_results: Optional[str]     # CVE lookup results
    report: Optional[str]          # Final findings report
    next_action: Optional[str]     # What the LLM decided to do next
    messages: List[str]            # Log of what's happened so far