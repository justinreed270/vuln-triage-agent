# Vulnerability Triage Agent

An autonomous security agent that accepts a target IP, orchestrates its own tool execution, and produces a professional findings report — without being told what to do at each step.

Built with LangGraph + Ollama. Runs entirely on local hardware. No cloud dependencies.

---

## What Problem This Solves

Security triage is repetitive: scan a target, look up what you found, write a report. A junior analyst can spend an hour on a workflow that produces the same structured output every time. This agent automates that first pass — scan, CVE lookup, report — so the analyst's time starts at interpretation, not data collection.

The design choice to run locally matters: sensitive target data never leaves the network. That constraint rules out cloud-based alternatives for most enterprise and government environments.

---

## Demo

```
python main.py 127.0.0.1
```

```
 Starting vulnerability triage for: 127.0.0.1

  [PLANNER] Next action: run_nmap
  [NMAP] Completed scan of 127.0.0.1
  [PLANNER] Next action: lookup_cves
  [CVE LOOKUP] Found 9 potential vulnerabilities
  [PLANNER] Next action: write_report
  [REPORT] Final report generated
  [PLANNER] Next action: done

 Markdown saved: reports/report_127_0_0_1_20260304_0448.md
 PDF saved:      reports/report_127_0_0_1_20260304_0448.pdf
```

Findings include real CVEs with CVSS scores pulled live from the NIST NVD API. Reports are saved automatically to a `/reports` folder that creates itself on first run.

> !!! >> Only scan targets you have explicit permission to scan. `scanme.nmap.org` is provided by Nmap for legal testing.

---

## Architecture

The agent runs a planner-executor loop. There is no hardcoded execution order.

```
[START] → [Planner] ──→ [Nmap Scan]    ──┐
                  ↑──→ [CVE Lookup]   ──┤→ [Planner] → ... → [END]
                  └──→ [Report Writer] ──┘
```

After every tool completes, control returns to the planner. The LLM reads the current state — what's been done, what hasn't — and decides what to call next. When everything is done, it routes to END.

This is the same planner-executor pattern used in production agentic systems. The tools are interchangeable; the loop is not specific to security work.

**State** is a shared TypedDict passed between every node. Each node reads from it and writes back to it. No node communicates directly with another.

**The planner** receives a 3-line status summary, not raw data. Keeping the input minimal reduces token cost and improves routing reliability.

**CVE extraction** is LLM-driven rather than regex-based. The model translates nmap output like `Apache httpd 2.4.7 ((Ubuntu))` into `Apache HTTP Server 2.4.7` — a query that actually returns NVD results. Regex breaks on output variance; the LLM handles it.

---

## Stack

| Component | Tool |
|---|---|
| Agent framework | LangGraph |
| LLM backend | Ollama (local) |
| Model | Llama 3.1 8B |
| Network scanning | Nmap |
| CVE data | NIST NVD API (free, unauthenticated) |
| Hardware | RTX 3090 24GB (Thunderbolt 4 eGPU) |

---

## Setup

**Prerequisites:** Python 3.10+, [Ollama](https://ollama.com), [Nmap](https://nmap.org/download.html) in PATH

```bash
git clone https://github.com/YOUR_USERNAME/vuln-triage-agent
cd vuln-triage-agent
python -m venv venv
venv\Scripts\activate        # Windows
pip install langgraph langchain-ollama langchain-core requests fpdf2
ollama pull llama3.1:8b
```

**Run:**
```bash
python main.py 127.0.0.1          # scan localhost
python main.py 192.168.1.1        # scan a network target
python main.py scanme.nmap.org    # scan Nmap's legal test host
```

Reports are saved to `/reports` as `.md` and `.pdf`. Delete the folder to clear all reports — it recreates itself on the next run.

---

## Known Issues

**PDF rendering** — fpdf2 occasionally drops report body content when the LLM output contains complex markdown patterns (nested bold, numbered lists with inline formatting). The `.md` file always renders correctly and can be exported to PDF via VS Code, Pandoc, or any markdown viewer. PDF output is a known iteration item.

**NVD rate limiting** — without an API key, NIST NVD limits requests to 5 per 30 seconds. The agent caps lookups at 5 services per run. Register for a [free NVD API key](https://nvd.nist.gov/developers/request-an-api-key) and add it as a header to remove this constraint.

**CVE relevance** — the agent retrieves CVEs based on keyword search, not fingerprint matching. Some returned CVEs may not apply to the specific version detected. Results should be verified before acting on them.

---

## What's Next

- Replace keyword-based CVE lookup with `bind_tools()` structured tool calling — the LLM generates precise search parameters rather than free-text queries
- Add LangGraph checkpointing so long scans can resume after interruption
- Expand tool nodes: Shodan lookup, banner grabbing, threat intel feeds
- Fix PDF rendering by pre-processing LLM output into clean plain text before passing to fpdf2

---

## Why This Project

Built as a portfolio demonstration of agentic AI applied to real security workflows. The goal was to understand the architecture from scratch — state management, conditional routing, LLM-as-orchestrator — not to wrap an existing tool. The security application is real; the agent found CVE-2021-44224 (CVSS 8.2) on a live test target on the first run.
