import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

from tools import (
    get_panel,
    get_workstation_requirements,
    search_sop,
    record_event,
    escalate_to_supervisor
)


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set.")

client = genai.Client(api_key=API_KEY)

MODEL = "gemini-3.5-flash-lite"


# ============================================================
# SYSTEM INSTRUCTION
# ============================================================

SYSTEM_INSTRUCTION = """
You are the Shop-Floor AI Agent for a fictional cabinet production system.

Your job is to help an operator understand a production panel,
verify whether it belongs at the selected workstation, retrieve
relevant SOP information, answer questions using only available
data, and escalate unsafe or unsupported situations.

IMPORTANT RULES:

1. Production facts must come from the available tools.

2. Never invent panel information.

3. Never invent:
   - panel dimensions
   - materials
   - cabinet IDs
   - required operations
   - workstation requirements

4. Never invent machine settings such as:
   - spindle speed
   - feed rate
   - temperature
   - pressure
   - tooling parameters
   - drill sizes
   - machine-specific settings

5. SOP instructions must come from the search_sop tool.

6. If information is unavailable, clearly say that it is unavailable.

7. If the physical panel conflicts with system information:
   - tell the operator to STOP processing
   - escalate to a supervisor

8. If a panel is not found:
   - do not invent information
   - clearly state "Panel Not Found"

9. If the panel belongs to a different workstation:
   - tell the operator NOT to process it at the selected workstation
   - identify the correct workstation when possible

10. Use tools when production information is required.
    Do not guess.

11. You may need to call multiple tools before answering.
    Do not assume that one tool call is enough.

12. Keep responses concise and useful for a shop-floor operator.

13. When giving production instructions, mention the relevant
    source or SOP.

14. If the operator asks for unsupported machine parameters,
    do not provide a value. Explain that the parameter is not
    provided by the available SOP/data and recommend supervisor
    confirmation.

15. The physical panel label mismatch scenario is considered
    unsafe. Escalate it to a supervisor.

You are an assistant for a production environment.
Safety and data accuracy are more important than completing
the requested operation.
"""


# ============================================================
# TOOL DECLARATIONS
# ============================================================

get_panel_declaration = types.FunctionDeclaration(
    name="get_panel",
    description="""
    Retrieves structured production information for a panel.

    Use this whenever panel information is needed.
    Never invent panel information.
    """,
    parameters_json_schema={
        "type": "object",
        "properties": {
            "panel_code": {
                "type": "string",
                "description": "Production panel code, such as P-1001."
            }
        },
        "required": ["panel_code"]
    }
)


get_workstation_declaration = types.FunctionDeclaration(
    name="get_workstation_requirements",
    description="""
    Retrieves the supported operations for a workstation.

    Use this to determine whether a panel's required operation
    matches the selected workstation.
    """,
    parameters_json_schema={
        "type": "object",
        "properties": {
            "workstation_id": {
                "type": "string",
                "description": "Workstation ID, such as EDGE-01."
            }
        },
        "required": ["workstation_id"]
    }
)


search_sop_declaration = types.FunctionDeclaration(
    name="search_sop",
    description="""
    Searches the supplied SOP documents for relevant operator
    instructions and safety information.

    Use this instead of relying on general knowledge for SOP
    instructions or machine parameters.
    """,
    parameters_json_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Topic or question to search for in the SOP."
            }
        },
        "required": ["query"]
    }
)


record_event_declaration = types.FunctionDeclaration(
    name="record_event",
    description="""
    Records a production event such as a scan, question,
    verification result, or other relevant activity.
    """,
    parameters_json_schema={
        "type": "object",
        "properties": {
            "event_type": {
                "type": "string",
                "description": "Type of production event."
            },
            "description": {
                "type": "string",
                "description": "Description of the event."
            },
            "panel_code": {
                "type": "string",
                "description": "Panel code associated with the event, if known."
            }
        },
        "required": ["event_type", "description"]
    }
)


escalate_declaration = types.FunctionDeclaration(
    name="escalate_to_supervisor",
    description="""
    Escalates an unsafe or unresolved production issue to a supervisor.

    Use this when physical information conflicts with system data
    or when required information cannot be safely determined.
    """,
    parameters_json_schema={
        "type": "object",
        "properties": {
            "reason": {
                "type": "string",
                "description": "Reason for supervisor escalation."
            },
            "panel_code": {
                "type": "string",
                "description": "Panel code associated with the escalation, if known."
            }
        },
        "required": ["reason"]
    }
)


TOOLS = [
    types.Tool(
        function_declarations=[
            get_panel_declaration,
            get_workstation_declaration,
            search_sop_declaration,
            record_event_declaration,
            escalate_declaration
        ]
    )
]


# ============================================================
# PYTHON TOOL FUNCTIONS
# ============================================================

AVAILABLE_FUNCTIONS = {
    "get_panel": get_panel,
    "get_workstation_requirements": get_workstation_requirements,
    "search_sop": search_sop,
    "record_event": record_event,
    "escalate_to_supervisor": escalate_to_supervisor
}


# ============================================================
# AGENT
# ============================================================

def run_agent(user_message, workstation_id=None, panel_code=None):

    context = f"""
Selected workstation:
{workstation_id or "Not specified"}

Scanned panel code:
{panel_code or "Not specified"}

Operator request:
{user_message}
"""

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=SYSTEM_INSTRUCTION + "\n\n" + context
                )
            ]
        )
    ]

    trace = []

    # Prevent an endless tool-calling loop.
    MAX_STEPS = 10

    for step in range(MAX_STEPS):

        response = client.models.generate_content(
            model=MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                tools=TOOLS,

                # We want to manually execute tools so that
                # our application can record the tool trace.
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True
                )
            )
        )

        # ----------------------------------------------------
        # MODEL WANTS TO CALL TOOLS
        # ----------------------------------------------------

        if response.function_calls:

            # Preserve the model's function-call response.
            model_content = response.candidates[0].content

            contents.append(model_content)

            function_response_parts = []

            for function_call in response.function_calls:

                function_name = function_call.name
                function_args = dict(function_call.args)

                function = AVAILABLE_FUNCTIONS.get(function_name)

                # ------------------------------------------------
                # UNKNOWN TOOL
                # ------------------------------------------------

                if function is None:

                    result = {
                        "success": False,
                        "error": f"Unknown tool: {function_name}"
                    }

                    trace.append({
                        "tool": function_name,
                        "input": function_args,
                        "success": False,
                        "source": None
                    })

                # ------------------------------------------------
                # EXECUTE TOOL
                # ------------------------------------------------

                else:

                    try:

                        result = function(**function_args)

                        trace.append({
                            "tool": function_name,
                            "input": function_args,
                            "success": result.get("success", True),
                            "source": result.get("source")
                        })

                    except Exception as error:

                        result = {
                            "success": False,
                            "error": str(error)
                        }

                        trace.append({
                            "tool": function_name,
                            "input": function_args,
                            "success": False,
                            "source": None
                        })

                # ------------------------------------------------
                # SEND TOOL RESULT BACK TO GEMINI
                # ------------------------------------------------

                function_response_parts.append(
                    types.Part.from_function_response(
                        name=function_name,
                        response=result
                    )
                )

            # Add all tool results together.
            contents.append(
                types.Content(
                    role="user",
                    parts=function_response_parts
                )
            )

            # Continue the loop so Gemini can:
            #
            # 1. Read the tool results
            # 2. Decide whether another tool is needed
            # 3. Or produce the final answer
            continue

        # ----------------------------------------------------
        # MODEL HAS FINAL ANSWER
        # ----------------------------------------------------

        final_text = response.text

        if not final_text:
            final_text = (
                "The agent could not produce a final response."
            )

        return {
            "response": final_text,
            "trace": trace
        }

    # --------------------------------------------------------
    # MAX TOOL STEPS REACHED
    # --------------------------------------------------------

    return {
        "response": (
            "The agent could not complete the request within "
            "the allowed number of tool steps."
        ),
        "trace": trace
    }