export interface Panel {
  panel_code: string;
  cabinet_id: string;
  panel_name: string;
  dimensions: {
    length: number;
    width: number;
    thickness: number;
  };
  material: string;
  required_operation: string;
}

export interface TraceItem {
  tool: string;
  input: Record<string, unknown>;
  success: boolean;
  source: string | null;
}

export interface AgentResponse {
  success: boolean;
  response: string;
  trace: TraceItem[];
}

export interface HistoryItem {
  timestamp: string;
  event_type: string;
  description: string;
  panel_code: string | null;
}

export interface Workstation {
  workstation_id: string;
  name: string;
}