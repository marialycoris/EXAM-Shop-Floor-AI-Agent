import { useState } from "react";
import type { AgentResponse } from "../types";

interface Props {
  workstationId: string;
  panelCode: string;
  onAgentResponse: (result: AgentResponse) => void;
}

function AgentChat({ workstationId, panelCode, onAgentResponse }: Props) {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState("");

  async function askAgent() {
    if (!message.trim()) {
      return;
    }

    setLoading(true);
    setResponse("");

    try {
      const result = await fetch("http://127.0.0.1:5000/api/agent", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message,
          workstation_id: workstationId,
          panel_code: panelCode,
        }),
      });

      const data = await result.json();

      if (!result.ok) {
        console.error("Backend error:", data);

        setResponse(`Backend error: ${data.error || "Unknown server error"}`);

        return;
      }

      if (!data.success) {
        setResponse("The agent could not process the request.");
        return;
      }

      setResponse(data.response);
      onAgentResponse(data);
    } catch (error) {
      console.error(error);
      setResponse(
        "Unable to connect to the backend. Make sure Flask is running.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="chat-card">
      <div className="section-header">
        <h2>AI Assistant</h2>
        <span>Gemini Agent</span>
      </div>

      <div className="agent-response">
        {response ? (
          <p>{response}</p>
        ) : (
          <p className="muted">
            Ask a question about the selected panel or SOP.
          </p>
        )}
      </div>

      <div className="chat-input">
        <input
          type="text"
          placeholder="Ask about this panel..."
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter") {
              askAgent();
            }
          }}
        />

        <button onClick={askAgent} disabled={loading || !message.trim()}>
          {loading ? "Thinking..." : "Ask"}
        </button>
      </div>
    </div>
  );
}

export default AgentChat;
