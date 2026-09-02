import { useState } from "react";

import AgentChat from "./components/AgentChat";
import AgentTrace from "./components/AgentTrace";
import History from "./components/History";
import PanelInfo from "./components/PanelInfo";
import WorkstationSelector from "./components/WorkstationSelector";

import type {
  AgentResponse,
  HistoryItem,
  Panel,
  TraceItem,
  Workstation
} from "./types";

import "./App.css";


const WORKSTATIONS: Workstation[] = [
  {
    workstation_id: "EDGE-01",
    name: "Edge Banding"
  },
  {
    workstation_id: "DRILL-01",
    name: "Drilling"
  }
];


function App() {

  const [selectedWorkstation, setSelectedWorkstation] =
    useState("EDGE-01");

  const [panelCode, setPanelCode] = useState("");

  const [panel, setPanel] = useState<Panel | null>(null);

  const [trace, setTrace] = useState<TraceItem[]>([]);

  const [history, setHistory] = useState<HistoryItem[]>([]);

  const [scanLoading, setScanLoading] = useState(false);


async function scanPanel() {

  if (!panelCode.trim()) {
    return;
  }

  setScanLoading(true);
  setTrace([]);

  try {

    const panelResult = await fetch(
      `http://127.0.0.1:5000/api/panels/${panelCode}`
    );

    if (!panelResult.ok) {
      setPanel(null);

      setHistory((previous) => [
        {
          timestamp: new Date().toLocaleTimeString(),
          event_type: "SCAN",
          description: `Panel ${panelCode} was not found.`,
          panel_code: panelCode
        },
        ...previous
      ]);

      return;
    }

    const panelData = await panelResult.json();

    setPanel(panelData.panel);


    const agentResult = await fetch(
      "http://127.0.0.1:5000/api/agent",
      {
        method: "POST",

        headers: {
          "Content-Type": "application/json"
        },

        body: JSON.stringify({
          message: `Scan and verify panel ${panelCode}. Determine whether it belongs at the selected workstation and provide the relevant instructions.`,
          workstation_id: selectedWorkstation,
          panel_code: panelCode
        })
      }
    );

    const data: AgentResponse = await agentResult.json();

    setTrace(data.trace);


    setHistory((previous) => [
      {
        timestamp: new Date().toLocaleTimeString(),
        event_type: "SCAN",
        description: `Panel ${panelCode} scanned at ${selectedWorkstation}.`,
        panel_code: panelCode
      },
      ...previous
    ]);

  } catch (error) {

    console.error(error);

  } finally {

    setScanLoading(false);

  }
}


  function handleAgentResponse(result: AgentResponse) {

    setTrace(result.trace);

    setHistory((previous) => [
      {
        timestamp: new Date().toLocaleTimeString(),
        event_type: "QUESTION",
        description: "Operator asked the AI assistant a question.",
        panel_code: panelCode || null
      },
      ...previous
    ]);
  }


  return (
    <div className="app">

      <header className="app-header">

        <div>
          <h1>Shop-Floor AI Agent</h1>

          <p>
            Cabinet Production Assistant
          </p>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          Agent Online
        </div>

      </header>


      <main>

        <section className="controls">

          <WorkstationSelector
            workstations={WORKSTATIONS}
            selectedWorkstation={selectedWorkstation}
            onChange={setSelectedWorkstation}
          />


          <div className="form-group panel-input">

            <label htmlFor="panel-code">
              Panel Code
            </label>

            <div className="scan-input">

              <input
                id="panel-code"
                type="text"
                placeholder="e.g. P-1001"
                value={panelCode}
                onChange={(event) =>
                  setPanelCode(event.target.value)
                }
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    scanPanel();
                  }
                }}
              />

              <button
                onClick={scanPanel}
                disabled={scanLoading || !panelCode.trim()}
              >
                {scanLoading ? "Checking..." : "Scan"}
              </button>

            </div>

          </div>

        </section>


        <section className="main-grid">

          <div className="left-column">

            <PanelInfo panel={panel} />

            <AgentTrace trace={trace} />

          </div>


          <div className="right-column">

            <AgentChat
              workstationId={selectedWorkstation}
              panelCode={panelCode}
              onAgentResponse={handleAgentResponse}
            />

            <History history={history} />

          </div>

        </section>

      </main>

    </div>
  );
}

export default App;