# ABC Cabinet — Shop-Floor AI Agent

An AI-powered shop-floor assistant prototype for **ABC Cabinet** that helps operators verify panels, confirm workstation compatibility, retrieve relevant SOP instructions, and safely handle unsupported questions or production discrepancies.

The system demonstrates an **agentic workflow** where the LLM decides which tools to use based on the operator's request and the available production data.

---

## Project Links & Overview

| Item                         | Details                                    |
| ---------------------------- | ------------------------------------------ |
| **Demo URL**                 | `https://exam-shop-floor-ai-agent.vercel.app/`
| **LLM Provider**             | Google Gemini                              |
| **Model**                    | Gemini 3.5 Flash-Lite                      |
| **Agent Implementation**     | Custom Python tool-calling agent           |
| **Frontend**                 | React + TypeScript + Vite                  |
| **Backend**                  | Python + Flask                             |
| **Data Storage**             | Structured JSON files + Markdown SOP files |
| **Approximate Time Spent**   | Approximately 1–2 hours                    |

---

## Features

* Select a shop-floor workstation
* Enter a panel code
* Retrieve production information for a panel
* Verify whether the panel belongs at the selected workstation
* Retrieve relevant SOP information
* Ask natural-language questions about the panel or SOP
* Prevent unsupported machine-setting answers
* Escalate safety-critical discrepancies to a supervisor
* Record scan and escalation events
* Display an agent tool trace showing which tools were called
* Handle unknown panels without inventing production data

---

## Architecture

```text
┌──────────────────────┐
│   React Frontend     │
│   TypeScript + Vite  │
└──────────┬───────────┘
           │
           │ HTTP / JSON
           ▼
┌──────────────────────┐
│     Flask Backend    │
│                      │
│     Agent Loop       │
└──────────┬───────────┘
           │
           │ Tool Calls
           ▼
┌──────────────────────────────────────┐
│              AI Agent                │
│                                      │
│        Google Gemini LLM             │
│                                      │
│   Decides which tool(s) to call      │
└──────────┬───────────────────────────┘
           │
     ┌─────┼─────────────────────────┐
     │     │          │              │
     ▼     ▼          ▼              ▼
  Panel  Workstation  SOP         Event /
  Data     Data       Search     Escalation
     │     │          │              │
     ▼     ▼          ▼              ▼
 panels.json  workstations.json  *.md  Event Log
```

---

## Agent Workflow

The agent follows the required agentic workflow:

```text
Operator Input
      ↓
   Gemini
      ↓
 Decide what information is needed
      ↓
   Call Tool
      ↓
 Read Tool Result
      ↓
 Decide whether another tool is needed
      ↓
 Call another tool if necessary
      ↓
 Generate grounded response
      ↓
 Respond to Operator
```

The sequence of tools is **not hardcoded**. The LLM can decide which available tool is appropriate based on the operator's question and the information returned by previous tools.

For example, a normal panel verification may result in:

```text
get_panel
      ↓
get_workstation_requirements
      ↓
search_sop
      ↓
record_event
      ↓
final response
```

A wrong workstation scenario may only require:

```text
get_panel
      ↓
get_workstation_requirements
      ↓
final response
```

This demonstrates that the agent can make different tool decisions depending on the situation.

---

## Available Tools

### `get_panel(panel_code)`

Retrieves production information for a panel from the structured panel data.

Returns information such as:

* Panel code
* Cabinet ID
* Panel name
* Dimensions
* Material
* Required operation

---

### `get_workstation_requirements(workstation_id)`

Retrieves the capabilities and supported operations of a workstation.

This allows the agent to determine whether a panel's required operation matches the selected workstation.

---

### `search_sop(query)`

Searches the available Markdown SOP files for relevant instructions.

The SOP contains approved operator instructions and safety information.

---

### `record_event(...)`

Records events such as panel scans and verification activities.

The event log includes:

* Timestamp
* Event type
* Description
* Panel code

---

### `escalate_to_supervisor(...)`

Records a supervisor escalation when an issue cannot safely be resolved using the available information.

This is used for situations such as:

* Physical label/system discrepancies
* Unsupported machine parameters
* Other safety-critical issues

---

## Data Storage

The prototype intentionally uses simple structured files rather than a database or vector database.

### Production Data

Production information is stored in:

```text
backend/data/panels.json
backend/data/workstations.json
```

Example panel information:

```json
{
  "panel_code": "P-1001",
  "cabinet_id": "CAB-001",
  "panel_name": "Left Side Panel",
  "dimensions": {
    "length": 720,
    "width": 600,
    "thickness": 18
  },
  "material": "MDF",
  "required_operation": "EDGE_BANDING"
}
```

### SOP Data

SOP information is stored as Markdown:

```text
backend/sops/edge_banding.md
backend/sops/drilling.md
```

This keeps production facts and approved operating instructions separate from the LLM.

---

# Safety & Hallucination Prevention

The LLM is **not treated as the source of production truth**.

Production facts such as:

* Panel codes
* Cabinet IDs
* Panel names
* Dimensions
* Materials
* Required operations
* Workstation capabilities

come from structured data.

SOP instructions come from the approved SOP files.

The LLM is primarily responsible for interpreting the operator's request, deciding which tools are needed, and presenting the retrieved information.

If required information is unavailable, the agent should not invent it.

For example, the prototype does not provide machine-specific settings such as:

* Spindle speeds
* Feed rates
* Temperatures
* Other unsupported machine parameters

When such information is requested, the agent tells the operator that the information is unavailable and recommends contacting a supervisor.

---


# Project Structure

```text
shop-floor-ai-agent/
│
├── backend/
│   ├── app.py
│   ├── agent.py
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── panel_tools.py
│   │   ├── workstation_tools.py
│   │   ├── sop_tools.py
│   │   └── event_tools.py
│   │
│   ├── data/
│   │   ├── panels.json
│   │   └── workstations.json
│   │
│   └── sops/
│       ├── edge_banding.md
│       └── drilling.md
│
├── frontend/
│   └── React + TypeScript application
│
├── .env
├── .gitignore
└── README.md
```
## Setup Instructions

### Prerequisites

Before running the project, make sure you have:

* Python 3.10+
* Node.js 20+
* npm
* A Google Gemini API key

---

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL_HERE
cd shop-floor-ai-agent
```

---

### 2. Set Up the Backend

Navigate to the backend directory:

```bash
cd backend
```

Create and activate a Python virtual environment:

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

---

### 3. Configure the Gemini API Key

Create a `.env` file in the **project root**:

```text
shop-floor-ai-agent/
├── backend/
├── frontend/
├── .env
└── README.md
```

Add the Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

The `.env` file is excluded from Git and should never be committed to the repository.

---

### 4. Start the Flask Backend

From the `backend` directory:

```bash
python app.py
```

The backend will run locally at:

```text
http://127.0.0.1:5000
```

---

### 5. Set Up the Frontend

Open another terminal and navigate to the frontend:

```bash
cd frontend
```

Install the frontend dependencies:

```bash
npm install
```

Start the Vite development server:

```bash
npm run dev
```

Vite will provide a local URL, typically:

```text
http://localhost:5173
```

Open the provided URL in a browser to use the application.

---

# Technology Stack

### Frontend

* React
* TypeScript
* Vite

### Backend

* Python
* Flask
* Flask-CORS

### AI

* Google Gemini
* Gemini 3.5 Flash-Lite
* Gemini function/tool calling

### Data

* JSON
* Markdown
* In-memory event history

### Deployment

* Vercel

---

# Conclusion

The ABC Cabinet Shop-Floor AI Agent demonstrates how an LLM can assist shop-floor operators while keeping production facts grounded in structured data and approved SOPs.

The prototype focuses on **safe, explainable tool use** rather than allowing the LLM to independently invent production information. It can verify panels, detect workstation mismatches, retrieve SOP instructions, refuse unsupported machine parameters, handle unknown panels, and escalate safety-critical discrepancies to a supervisor.
