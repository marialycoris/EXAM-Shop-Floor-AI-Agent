import type { HistoryItem } from "../types";

interface Props {
  history: HistoryItem[];
}

function History({ history }: Props) {
  return (
    <div className="history-card">
      <div className="section-header">
        <h2>History</h2>
      </div>

      {history.length === 0 ? (
        <p className="muted">No activity yet.</p>
      ) : (
        <div className="history-list">
          {history.map((item, index) => (
            <div className="history-item" key={`${item.timestamp}-${index}`}>
              <span className="history-time">
                {item.timestamp}
              </span>

              <div>
                <strong>{item.event_type}</strong>
                <p>{item.description}</p>

                {item.panel_code && (
                  <small>Panel: {item.panel_code}</small>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default History;