import os
import re
import time
import json
import threading
import streamlit as st

# Direct import of investigation runner
from adk_investigator import run_investigation, set_status

st.set_page_config(page_title="Autonomous Incident Observer", layout="wide", page_icon="🕵️")

st.markdown("""
<style>
    .report-card { border-radius: 8px; padding: 1.2rem; background-color: #f8f9fa; border-left: 5px solid #0d6efd; margin-bottom: 1rem; }
    .status-badge { display: inline-block; padding: 0.4rem 0.9rem; border-radius: 14px; font-weight: bold; font-size: 0.95rem; }
    .status-active { background-color: #d1e7dd; color: #0f5132; border: 1px solid #a3cfbb; }
    .status-waiting { background-color: #fff3cd; color: #664d03; border: 1px solid #ffe69c; }
    .status-running { background-color: #cfe2ff; color: #084298; border: 1px solid #b6d4fe; }
    .status-anomaly { background-color: #f8d7da; color: #842029; border: 1px solid #f5c2c7; }
</style>
""", unsafe_allow_html=True)

REPORT_FILE = "INCIDENT_REPORT.md"
STATUS_FILE = ".agent_status"

def extract_mermaid(markdown_text):
    """Extracts raw mermaid code block from markdown text if present."""
    match = re.search(r"```mermaid\s*\n(.*?)\n```", markdown_text, re.DOTALL)
    if match:
        clean_mermaid = match.group(1).strip()
        body_without_mermaid = re.sub(r"```mermaid\s*\n.*?\n```", "", markdown_text, flags=re.DOTALL)
        return clean_mermaid, body_without_mermaid
    return None, markdown_text

def read_status():
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None

st.sidebar.title("🎮 Hackathon Control Panel")
st.sidebar.caption("Single-screen controls for MacBook Air")

# Interactive Controls for Single-Screen Presentation
if st.sidebar.button("🚀 Dispatch Autonomous Agent", type="primary", use_container_width=True):
    # Clear old report so the stage progress is visible
    if os.path.exists(REPORT_FILE):
        try:
            os.remove(REPORT_FILE)
        except Exception:
            pass

    # Immediately mark inspecting state so the browser turns blue right now
    set_status("inspecting", "Initializing Autonomous SRE Investigator...", step=1, total=3)

    # Launch agent in background thread
    thread = threading.Thread(target=run_investigation, daemon=True)
    thread.start()
    st.sidebar.success("Agent dispatched!")
    st.rerun()

if st.sidebar.button("🔄 Reset Demo State", use_container_width=True):
    if os.path.exists(REPORT_FILE):
        try:
            os.remove(REPORT_FILE)
        except Exception:
            pass
    if os.path.exists(STATUS_FILE):
        try:
            os.remove(STATUS_FILE)
        except Exception:
            pass
    st.sidebar.info("Demo state reset to 'Waiting'.")
    st.rerun()

st.sidebar.divider()
auto_refresh = st.sidebar.checkbox("Live Polling (Watchdog)", value=True)
poll_interval = st.sidebar.slider("Poll Interval (seconds)", 0.2, 2.0, 0.5, step=0.1)

st.title("🛰️ Live Agentic Incident Watcher")
st.caption("Autonomous SRE Network Investigator (Google ADK & Gemini 3.8 Flash)")

placeholder = st.empty()

while True:
    with placeholder.container():
        file_exists = os.path.exists(REPORT_FILE)
        status_info = read_status()

        if not file_exists:
            if status_info and status_info.get("state") in ["inspecting", "analyzing", "reasoning"]:
                state = status_info.get("state")
                msg = status_info.get("message", "Agent running...")
                step = status_info.get("step", 1)
                total = status_info.get("total", 3)

                badge_class = "status-running" if state != "analyzing" else "status-anomaly"
                badge_icon = "🔎" if state == "inspecting" else ("⚠️" if state == "analyzing" else "🧠")

                st.markdown(f'<span class="status-badge {badge_class}">{badge_icon} AGENT ENGAGED: {msg}</span>', unsafe_allow_html=True)
                st.progress(step / total, text=f"Investigation Pipeline: Step {step} of {total}")
                st.info("The Autonomous SRE Agent is actively processing the wire capture...")
            else:
                st.markdown('<span class="status-badge status-waiting">⏳ Waiting for Agent Execution...</span>', unsafe_allow_html=True)
                st.info(f"Targeting `{REPORT_FILE}`. Click **'🚀 Dispatch Autonomous Agent'** in the sidebar (or run `python adk_investigator.py` in terminal) to begin.")
        else:
            mod_time = time.ctime(os.path.getmtime(REPORT_FILE))
            st.markdown(f'<span class="status-badge status-active">🟢 Incident Triage Artifact Detected</span> &nbsp; *(Published: {mod_time})*', unsafe_allow_html=True)

            with open(REPORT_FILE, "r", encoding="utf-8") as f:
                content = f.read()

            if not content.strip():
                st.warning("File created, awaiting agent write stream...")
            else:
                mermaid_code, clean_body = extract_mermaid(content)

                col_diag, col_text = st.columns([1, 1])

                with col_diag:
                    st.subheader("📊 Reconstructed Flow")
                    if mermaid_code:
                        html_mermaid = f"""
                        <div class="mermaid">
                        {mermaid_code}
                        </div>
                        <script type="module">
                            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                            mermaid.initialize({{ startOnLoad: true, theme: 'neutral' }});
                        </script>
                        """
                        st.components.v1.html(html_mermaid, height=520, scrolling=True)
                    else:
                        st.info("No Mermaid sequence block detected in report yet.")

                with col_text:
                    st.subheader("📝 Live Triage & Remediation")
                    st.markdown(clean_body)

    if not auto_refresh:
        break
    time.sleep(poll_interval)
