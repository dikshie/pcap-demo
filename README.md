# 🕵️ Autonomous SRE Network Investigator (Powered by Google ADK)

> **Autonomous, privacy-first network incident diagnosis powered by Google ADK (`google-adk`), Gemini 3.8 Flash, and Scapy.**

An AI-driven Site Reliability Engineering (SRE) agent that autonomously inspects suspicious packet captures (`.pcap`), detects wire-level anomalies (such as spoofed TCP Resets and TTL discrepancies), reconstructs interactive Mermaid.js sequence diagrams, and generates actionable firewall mitigation policies in real time.

---

## 🌟 Hackathon Elevator Pitch (30 Seconds)

> *"When production connections drop mysteriously, network engineers spend hours sifting through thousands of Wireshark packets. Traditional LLMs can't help because uploading packet captures violates security compliance, and raw PCAPs exceed context limits.*
>
> *We built the **Autonomous SRE Network Investigator** using **Google ADK** and **Gemini 3.8 Flash**. It keeps raw packet payloads strictly local, computes deterministic wire telemetry with Scapy, autonomously reasons through subtle anomalies (like intermediate hop TTL mismatches), and live-streams an actionable incident triage report with reconstructed Mermaid sequence diagrams into a real-time Streamlit dashboard."*

---

## 🏛️ System Architecture

```mermaid
flowchart LR
    subgraph Local Machine [🔒 Secure Local Perimeter - Zero Payload Leakage]
        PCAP["Incident Capture\nsamples/*.pcap"] --> Tools["agent_tools.py\n(Scapy Parser & TTL Tracker)"]
        Tools -->|Compact Telemetry\nJSON (No Raw Payloads)| ADK["adk_investigator.py\n(Google ADK LlmAgent)"]
    end

    subgraph Google Cloud [☁️ Gemini Intelligence]
        ADK <-->|Multi-turn Tool Calling\n& Reasoning Loop| Gemini["gemini-3.8-flash"]
    end

    subgraph Live Presentation [🖥️ Real-Time Observability]
        ADK -->|Writes Artifact| Report["INCIDENT_REPORT.md\n(Root Cause + Mermaid + Fix)"]
        Report -->|Watchdog Polling| Viewer["viewer.py\n(Streamlit Live Viewer)"]
    end
```

### Core Design Principles
1. **Zero-Trust Privacy Boundary**: Raw packet payloads are never sent to the LLM. Only aggregated flow metadata (5-tuples, flag counts, TTL statistics, flagged SNI domain strings) are exchanged.
2. **Deterministic Ground Truth**: Scapy computes facts (TTL distributions, RST flags, duplicate ACKs) before the agent reasons, preventing hallucinated telemetry.
3. **Google ADK Code-First Agent**: Native multi-turn tool calling via `google-adk`'s `LlmAgent` and `Runner`, orchestrating the investigation workflow autonomously.
4. **Live Artifact Watcher**: Streamlit observes the agent's filesystem outputs via real-time polling, updating the audience with interactive Mermaid diagrams the moment the agent finishes reasoning.

---

## 📂 Repository Structure

```
~/VIRTUAL/pcap-demo/
├── adk_investigator.py       # Google ADK Agent (LlmAgent + pcap_tool binding)
├── agent_tools.py           # Scapy packet parser, TTL analysis, and TLS SNI extractor
├── viewer.py                # Streamlit real-time incident dashboard with Mermaid rendering
├── INCIDENT_REPORT.md       # Agent-generated incident report (live artifact)
├── samples/                 # Sample incident PCAPs
│   └── 03_firewall_rst_injection.pcap # DPI Firewall RST injection incident
├── data/                    # Reserved exclusively for local PCAPs (git-ignored)
├── .env                     # GEMINI_API_KEY configuration
├── requirements.txt         # Project dependencies
└── README.md                # Hackathon presentation and setup guide
```

---

## ⚡ Quickstart & Setup

### 1. Prerequisites
- macOS / Linux
- Python 3.14 (or Python 3.10+)
- [uv](https://github.com/astral-sh/uv) (recommended) or standard `pip`

### 2. Installation
```bash
cd ~/VIRTUAL/pcap-demo

# Create virtual environment if needed
uv venv --python 3.14
source bin/activate

# Install dependencies
uv pip install google-adk google-genai streamlit scapy python-dotenv pydantic
```

### 3. API Key Configuration
Create or edit `.env` in the project root:
```env
GEMINI_API_KEY="your-gemini-api-key-here"
```

---

## 🎬 Live Hackathon Demo Walkthrough (Optimized for Single-Screen MacBook Air)

You do **not** need an external monitor. You can deliver this entire demonstration seamlessly directly on your **MacBook Air M2** using either of two presentation modes:

### Mode A: The "One-Tab" Dashboard (Recommended for Laptop Only)
You only keep **one full-screen browser window open** ([http://localhost:8501](http://localhost:8501)) in front of the judges:
1. Click **"🔄 Reset Demo State"** in the left sidebar $\rightarrow$ The UI turns amber: `⏳ Waiting for Agent Execution...`.
2. Click **"🚀 Dispatch Autonomous Agent"** in the sidebar.
3. The live staged progress bar immediately animates directly on your MacBook screen:
   * `🔎 Ingesting & parsing wire frames via Scapy...` (Phase 1)
   * `⚠️ Flagged Anomaly: Server TTL 128 vs Injected RST TTL 64` (Phase 2)
   * `🧠 Gemini 3.8 Flash synthesizing report...` (Phase 3)
4. The dashboard turns green, rendering the interactive **Mermaid.js sequence diagram** and remediation side-by-side!

---

### Mode B: macOS Split View / Trackpad Swipe
If judges ask to see terminal execution:
* **macOS Split View**: Tile your Terminal to the left half and Chrome/Safari to the right half by holding the green window maximize button.
* **3-Finger Swipe**: Run `./bin/python adk_investigator.py` on Space 1, then swipe 3 fingers right on your MacBook Air trackpad to Space 2 to watch the live viewer react.

---

### Step 1: Start the Live Viewer
In the background or a separate terminal tab:
```bash
cd ~/VIRTUAL/pcap-demo
streamlit run viewer.py
```
Open **[http://localhost:8501](http://localhost:8501)** in your browser.

---

### Step 2: Show the "Waiting State" (The Hook)
Reset the workspace before bringing the judges' attention to the screen:
```bash
rm -f INCIDENT_REPORT.md .agent_status
```
👉 **Point to the right screen**: The dashboard immediately displays:
> **`⏳ Waiting for Agent Execution... Targeting INCIDENT_REPORT.md`**

**Talking Point for Judges**:
> *"Our incident observer is actively monitoring our cloud and edge perimeters. Right now, our monitoring systems alerted us to connection terminations, and an incident capture was dropped into `samples/`. We are about to deploy our autonomous Google ADK agent to investigate."*

---

### Step 3: Trigger the Autonomous SRE Agent (The Investigation Pacing)
In your left terminal, run:
```bash
cd ~/VIRTUAL/pcap-demo
./bin/python adk_investigator.py
```

**What the Audience & Judges See**:
The execution is paced with clear visual stages so you can guide the judges through each phase:

1. **Phase 1 — Wire Perception (`[Scene 2: Ingest]`)**:
   * **Terminal**: `🛰️ Ingesting and parsing wire frames from samples/03_firewall_rst_injection.pcap...`
   * **Streamlit Viewer**: Displays blue badge: `🔎 AGENT ENGAGED: Ingesting & parsing wire frames via Scapy...` with an active progress bar.
   * **Presenter**: *"Notice the agent is invoking our Scapy perception tool locally—raw payloads never leave this machine."*

2. **Phase 2 — Anomaly Detection (`[Scene 2: Perceive]`)**:
   * **Terminal**: Prints server baseline TTL (`128`) vs injected RST TTL (`64`), plus flagged SNI (`restricted-vault.corp.internal`).
   * **Streamlit Viewer**: Switches to a high-priority warning badge: `⚠️ AGENT ENGAGED: Flagged Anomaly! Legitimate Server TTL=128 vs Injected RST TTL=64`.
   * **Presenter**: *"The agent immediately flags the smoking gun: legitimate server packets have TTL 128, but the connection dropped on an RST packet with TTL 64. That is the physical fingerprint of middlebox injection."*

3. **Phase 3 — Agentic Reasoning (`[Scene 3: Reason]`)**:
   * **Terminal**: `🧠 Dispatching telemetry to Gemini 3.8 Flash via Google ADK...`
   * **Streamlit Viewer**: Displays: `🧠 AGENT ENGAGED: Gemini 3.8 Flash synthesizing root cause, Mermaid diagram, and firewall rules...`
   * **Presenter**: *"Google ADK passes the structured telemetry to Gemini 3.8 Flash to synthesize the incident root cause and generate executable remediation commands."*

---

### Step 4: The "Aha!" Moment (The Reveal)
Within seconds:
1. **The Viewer turns vibrant green**: `🟢 Incident Triage Artifact Detected`.
2. **Interactive Mermaid Sequence Diagram**: Animates on screen showing the Client, Inline DPI Firewall, and Server.
3. **Instant Mitigation Policies**: Ready-to-copy `firewall-cmd` and `nftables` commands.

---

## 🔬 Incident Deep-Dive: How the Agent Discovered the Bug

### The Anomaly
```text
Packet #1: 10.0.1.15:52344  -> 203.0.113.80:443  [SYN]      TTL=64   (Client)
Packet #2: 203.0.113.80:443 -> 10.0.1.15:52344   [SYN, ACK] TTL=128  (Legitimate Server)
Packet #3: 10.0.1.15:52344  -> 203.0.113.80:443  [ACK]      TTL=64   (Client)
Packet #4: 10.0.1.15:52344  -> 203.0.113.80:443  [PSH, ACK] TTL=64   (TLS Client Hello w/ SNI)
Packet #5: 203.0.113.80:443 -> 10.0.1.15:52344   [RST]      TTL=64   ⚠️ (INJECTED BY MIDDLEBOX!)
```

### The Reasoning
1. **Server Baseline TTL**: The genuine web server at `203.0.113.80` operates with an IP Time-To-Live (TTL) of **128**.
2. **The Spoofed Reset**: Packet #5 claims to originate from `203.0.113.80`, yet its IP header displays **TTL=64**. Packets traversing the internet from the same remote host cannot gain 64 hops.
3. **The Trigger**: The reset was transmitted within **2 milliseconds** of the client issuing a TLS Client Hello containing the SNI `restricted-vault.corp.internal`.
4. **The Verdict**: An inline Deep Packet Inspection (DPI) firewall inspected the plaintext SNI header, matched a security blacklist, and injected a spoofed TCP RST toward the client to terminate the socket.

---

## 🏆 Judge FAQ (Defending Your Architecture)

### Q: Why use Google ADK instead of a standard Gemini prompt?
> **Answer**: *"Google ADK (`google-adk`) is a code-first agent framework that provides native function calling, agent state management, and multi-turn execution loops. Instead of an all-in-one text generation prompt, ADK allows the agent to iteratively perceive data, invoke tools conditionally, and produce standardized artifacts without brittle glue code."*

### Q: How does this maintain enterprise data privacy?
> **Answer**: *"Raw enterprise packet payloads never leave the host perimeter. Scapy extracts only mathematical telemetry (sequence deltas, flag counts, TTL sets) locally. Gemini only receives abstracted telemetry JSON, strictly adhering to SOC2, HIPAA, and GDPR compliance."*

### Q: How extensible is this to other network problems?
> **Answer**: *"Because `agent_tools.py` provides modular detectors, we can easily add detection for MTU blackholes (duplicate ACKs > 3), TCP zero-window stalls, BGP route flaps, or DNS NXDOMAIN amplification attacks simply by adding Python functions to the ADK agent's toolbelt."*

---

## 🛠️ Verification & Test Commands

To verify your environment before stepping on stage:

```bash
# 1. Test Scapy tool directly
./bin/python agent_tools.py samples/03_firewall_rst_injection.pcap

# 2. Test Streamlit HTTP endpoint
curl -I http://localhost:8501

# 3. Test full agent execution
./bin/python adk_investigator.py
```

---

*Built with ❤️ for the Google AI Agent Hackathon using Google ADK & Gemini 3.8 Flash.*
