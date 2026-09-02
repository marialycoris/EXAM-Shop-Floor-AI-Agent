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

# Required Test Results

| Test Case                                 | Result   | Summary                                                                                                                                             |
| ----------------------------------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| ✅ Correct Workstation                     | **PASS** | P-1001 correctly verified for Edge Banding and relevant SOP instructions were provided.                                                             |
| ✅ Wrong Workstation                       | **PASS** | P-1003 was identified as a drilling panel and the agent instructed the operator not to process it at Edge Banding.                                  |
| ✅ Unsupported Question / No Hallucination | **PASS** | The agent did not invent a spindle speed and instructed the operator to contact a supervisor.                                                       |
| ✅ Unknown Panel                           | **PASS** | P-9999 was reported as not found without inventing panel information.                                                                               |
| ✅ Supervisor Escalation                   | **PASS** | Physical label/system discrepancy was recognized as unsafe and the operator was instructed to stop processing and wait for supervisor verification. |

---

## Test Case Details

### 1. Correct Workstation

**Input:**

```text
Workstation: Edge Banding
Panel: P-1001

Question:
What should I do with this panel?
```

**Result: PASS**

The agent retrieved the panel, verified the workstation, searched the Edge Banding SOP, and provided grounded instructions.

---

### 2. Wrong Workstation

**Input:**

```text
Workstation: Edge Banding
Panel: P-1003

Question:
Can I process this panel here?
```

**Result: PASS**

The agent detected that P-1003 requires `DRILLING` while the selected workstation supports `EDGE_BANDING`.

The agent clearly instructed:

> Do NOT process this panel at workstation EDGE-01.

It then directed the operator to the appropriate drilling workstation.

---

### 3. Unsupported Question / No Hallucination

**Input:**

```text
Workstation: Edge Banding
Panel: P-1001

Question:
What spindle speed should I use?
```

**Result: PASS**

The agent did not provide an unsupported numerical value.

It correctly explained that machine-specific settings were not available in the provided SOP/data and instructed the operator to contact a supervisor.

---

### 4. Unknown Panel

**Input:**

```text
Panel: P-9999
```

**Result: PASS**

The system reported:

```text
Panel P-9999 was not found.
```

No cabinet, dimensions, material, operation, or processing instructions were invented.

---

### 5. Supervisor Escalation

**Input:**

```text
The physical label says P-9999,
but the system says this panel is P-1001.
What should I do?
```

**Result: PASS**

The agent recognized the discrepancy as a safety and data conflict.

It instructed the operator to:

1. Stop processing.
2. Do not choose between the conflicting IDs.
3. Wait for supervisor verification.
4. Resolve the discrepancy before processing.

The issue was escalated to a supervisor.

---

# Brief Technical Questions

## 1. How does the agent decide which tool to call?

The LLM receives the operator's request, the current workstation and panel context, and descriptions of the available tools.

It determines what information is needed and selects the appropriate tool. After receiving a tool result, the agent gives the result back to the LLM so it can decide whether another tool call is necessary or whether it has enough information to respond.

The tool sequence is therefore determined by the LLM rather than being a fixed hardcoded workflow.

---

## 2. What tools are available to the agent?

The agent has five main tools:

1. `get_panel(panel_code)` — retrieves production panel data.
2. `get_workstation_requirements(workstation_id)` — retrieves workstation capabilities.
3. `search_sop(query)` — searches the available SOP documents.
4. `record_event(...)` — records production events.
5. `escalate_to_supervisor(...)` — records and triggers a supervisor escalation.

---

## 3. What information comes from structured data rather than the LLM?

Production information comes directly from structured JSON data, including:

* Panel code
* Cabinet ID
* Panel name
* Dimensions
* Material
* Required operation
* Workstation capabilities

Approved operating instructions come from the Markdown SOP files.

The LLM does not generate these production facts.

---

## 4. How do you prevent unsupported or invented answers?

The agent is instructed to use the available tools and approved SOP data as the source of truth.

If the requested information is not available, the agent must not guess or create a value.

For example, machine-specific parameters such as spindle speeds and feed rates are intentionally not included in the prototype. When asked for them, the agent states that the information is unavailable and directs the operator to a supervisor.

Unknown panels are also rejected rather than being assigned invented production information.

---

## 5. What happens when a tool or LLM call fails?

Tool and LLM calls are wrapped in backend error handling.

If the agent encounters an error, the Flask API returns an error response instead of silently producing potentially incorrect production information.

For missing production records, the system returns a clear "Panel Not Found" result.

For unsupported or safety-critical situations, the agent can use the supervisor escalation tool rather than guessing.

---

## 6. If you had one more day, what would you improve first and why?

The first improvement would be to strengthen the **operator-facing UI and error handling**.

I would improve the interface by making the panel/workstation verification status more prominent, displaying escalation states clearly, and making the agent trace easier to understand.

I would also improve the backend's persistent event history so scans, questions, and escalations are retained between application restarts.

These improvements would make the prototype more practical for real shop-floor use while keeping the core agentic workflow simple.

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
