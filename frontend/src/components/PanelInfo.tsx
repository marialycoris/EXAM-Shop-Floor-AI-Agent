import type { Panel } from "../types";

interface Props {
  panel: Panel | null;
}

function PanelInfo({ panel }: Props) {
  if (!panel) {
    return (
      <div className="panel-card empty-state">
        <p>No panel scanned.</p>
        <span>Enter a panel code and select Scan.</span>
      </div>
    );
  }

  return (
    <div className="panel-card">
      <div className="section-header">
        <h2>Panel Information</h2>
        <span className="panel-code">{panel.panel_code}</span>
      </div>

      <div className="panel-details">
        <div>
          <span>Cabinet ID</span>
          <strong>{panel.cabinet_id}</strong>
        </div>

        <div>
          <span>Panel Name</span>
          <strong>{panel.panel_name}</strong>
        </div>

        <div>
          <span>Dimensions</span>
          <strong>
            {panel.dimensions.length} × {panel.dimensions.width} ×{" "}
            {panel.dimensions.thickness} mm
          </strong>
        </div>

        <div>
          <span>Material</span>
          <strong>{panel.material}</strong>
        </div>

        <div>
          <span>Required Operation</span>
          <strong>{panel.required_operation.replace("_", " ")}</strong>
        </div>
      </div>
    </div>
  );
}

export default PanelInfo;