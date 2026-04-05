# AI-Paradox
AI Paradox is an intelligent, multi-agent triage system that transforms chaotic "brain dumps" into structured, prioritized, and executed real-world tasks using Google ADK and the Model Context Protocol (MCP)


# 🧠 AI Paradox: The Ultimate Brain-Dump Triage System

**Gen AI Academy APAC Edition - Hackthon Submission**

[![Built with Google ADK](https://img.shields.io/badge/Built_with-Google_ADK-blue?logo=google)](https://github.com/google/agent-development-kit)
[![Powered by Gemini](https://img.shields.io/badge/Powered_by-Gemini_2.5_Flash-orange?logo=googlebard)](https://ai.google.dev/)
[![Deployed on Cloud Run](https://img.shields.io/badge/Deployed_on-Google_Cloud_Run-blue?logo=googlecloud)](https://cloud.google.com/run)


**Live App URL:** https://ai-paradox-agent-926685116409.europe-west1.run.app

---

## 📌 The Problem
Modern professionals suffer from cognitive overload. We have chaotic, racing thoughts—massive project ideas, urgent to-dos, and scheduled meetings—all jumbled together. Manually dissecting these "brain-dumps" and sorting them into task managers, calendars, and note-taking apps takes too much time and energy.

## 🚀 The Solution: AI Paradox
**AI Paradox** is an empathetic, multi-agent AI router. You feed it a single, chaotic paragraph of text, and it autonomously reasons, prioritizes, and executes. 

It assesses your mental load, breaks down massive goals into micro-tasks, assigns priority levels (Eisenhower Matrix), and seamlessly integrates with a custom Model Context Protocol (MCP) server to save your structured data into a local database.

---

## 🏗️ Architecture & Core Workflows

Our system leverages a **Primary Coordinator Agent** routing to four highly specialized **Sub-Agents**, interacting with a custom **FastMCP** server.

1. **Greeter (Root Agent):** Captures the user's raw input.
2. **Wellness Agent:** Analyzes the prompt's tone. If the user sounds overwhelmed, it injects mandatory "Wellness Breaks" into the agenda.
3. **Project Manager Agent:** Identifies massive, multi-step goals (e.g., "Launch my startup") and breaks them down into 3-4 actionable micro-tasks.
4. **Triage Agent (Eisenhower Matrix):** Evaluates the urgency of every task, tagging them as High, Medium, or Low priority. It then executes the **MCP Tools** to save the data.
5. **Response Formatter:** Synthesizes the execution results into a friendly, empathetic summary for the user.

### 🔌 Custom MCP Server (`nexus_mcp.py`)
To satisfy the MCP requirement, we built an open-source Python FastMCP server containing three core tools, connected to a structured SQLite database:
* `add_task(description, priority)`: Logs tasks to the `tasks` table with a 'PENDING' status.
* `add_note(content)`: Saves raw ideas to the `notes` table.
* `schedule_event(title, time)`: Simulates calendar scheduling.

---

## 💻 Tech Stack
* **Agent Framework:** Google Agent Development Kit (ADK)
* **LLM:** Gemini 2.5 Flash
* **Tooling Standard:** Model Context Protocol (FastMCP Python)
* **Database:** SQLite
* **Deployment:** Google Cloud Run (Serverless API & Web UI)
* **Package Manager:** `uv`

---

## 🛠️ Local Installation & Setup

**Prerequisites:**
* Python 3.11+
* `uv` package manager installed
* Google Gemini API Key

**Steps:**
1. Clone the repository:
   ```bash
   git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)
   cd ai-paradox
