import type { TraceItem } from "../types";

interface Props {
  trace?: TraceItem[];
}

function AgentTrace({ trace = [] }: Props) {
  return (
    <div className="trace-card">
      <div className="section-header">
        <h2>Agent Trace</h2>
        <span>{trace.length} tool calls</span>
      </div>

      {trace.length === 0 ? (
        <p className="muted">No tool calls yet.</p>
      ) : (
        <div className="trace-list">
          {trace.map((item, index) => (
            <div className="trace-item" key={`${item.tool}-${index}`}>
              <div className="trace-status">
                {item.success ? "✓" : "✕"}
              </div>

              <div className="trace-content">
                <strong>{item.tool}</strong>

                <code>
                  {JSON.stringify(item.input)}
                </code>

                {item.source && (
                  <span className="trace-source">
                    Source: {item.source}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default AgentTrace;