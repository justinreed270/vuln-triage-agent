# main.py
import os
from agent.graph import build_graph

def save_pdf(target, report_text, filename_base):
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos
    import re

    # Strip all markdown formatting before rendering
    def clean(text):
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # remove bold
        text = re.sub(r'\*(.*?)\*', r'\1', text)        # remove italic
        text = text.encode('latin-1', errors='replace').decode('latin-1')
        return text

    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=15)

    # Title
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(26, 82, 118)
    pdf.cell(0, 10, "Vulnerability Triage Report",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.set_font("Helvetica", "I", 11)
    pdf.set_text_color(127, 140, 141)
    pdf.cell(0, 8, f"Target: {target}",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(4)
    pdf.set_draw_color(46, 117, 182)
    pdf.set_line_width(0.5)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(6)

    # Body
    for line in report_text.splitlines():
        line = clean(line)
        if line.startswith("## "):
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(26, 82, 118)
            pdf.multi_cell(180, 7, line.replace("## ", ""))
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(30, 30, 30)
        elif line.startswith("# "):
            pdf.ln(3)
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_text_color(26, 82, 118)
            pdf.multi_cell(180, 8, line.replace("# ", ""))
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(30, 30, 30)
        elif line.startswith("* ") or line.startswith("- "):
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(30, 30, 30)
            pdf.multi_cell(180, 6, f"  - {line[2:].strip()}")
        elif line.strip() == "":
            pdf.ln(2)
        else:
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(30, 30, 30)
            pdf.multi_cell(180, 6, line)

        pdf_path = f"{filename_base}.pdf"
        pdf.output(pdf_path)
        return pdf_path

def run_triage(target: str):
    graph = build_graph()
    
    initial_state = {
        "target": target,
        "scan_results": None,
        "cve_results": None,
        "report": None,
        "next_action": None,
        "messages": []
    }
    
    print(f"\n Starting vulnerability triage for: {target}\n")
    
    # stream_mode="values" prints state after every node execution
    for step, state in enumerate(graph.stream(initial_state, stream_mode="values")):
        # Print the latest log message if there is one
        messages = state.get("messages", [])
        if messages:
            print(f"  {messages[-1]}")
        
        # Stop if we hit a runaway loop (safety valve)
        if step > 20:
            print("Safety limit reached — stopping.")
            break
    
    # Print final report
    final_report = state.get("report", "No report generated.")
    print("\n" + "="*60)
    print("FINAL VULNERABILITY TRIAGE REPORT")
    print("="*60)
    print(final_report)
    
    from datetime import datetime
    os.makedirs("reports", exist_ok=True)
    filename_base = f"reports/report_{target.replace('.','_')}_{datetime.now().strftime('%Y%m%d_%H%M')}"

    with open(f"{filename_base}.md", "w") as f:
        f.write(f"# Vulnerability Triage Report\n**Target:** {target}\n\n")
        f.write(final_report)

    pdf_path = save_pdf(target, final_report, filename_base)

    print(f"\n📄 Markdown saved: {filename_base}.md")
    print(f"📄 PDF saved: {pdf_path}")    

    return state

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    run_triage(target)
"""
Your folder structure should look like this:

vuln-triage-agent/
├── main.py
├── agent/
│   ├── __init__.py   ← empty file, makes it a package
│   ├── state.py
│   ├── planner.py
│   ├── tools.py
│   └── graph.py
"""