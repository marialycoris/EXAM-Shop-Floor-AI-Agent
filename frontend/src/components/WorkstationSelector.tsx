import type { Workstation } from "../types";

interface Props {
  workstations: Workstation[];
  selectedWorkstation: string;
  onChange: (value: string) => void;
}

function WorkstationSelector({
  workstations,
  selectedWorkstation,
  onChange
}: Props) {
  return (
    <div className="form-group">
      <label htmlFor="workstation">Workstation</label>

      <select
        id="workstation"
        value={selectedWorkstation}
        onChange={(event) => onChange(event.target.value)}
      >
        {workstations.map((workstation) => (
          <option
            key={workstation.workstation_id}
            value={workstation.workstation_id}
          >
            {workstation.name}
          </option>
        ))}
      </select>
    </div>
  );
}

export default WorkstationSelector;