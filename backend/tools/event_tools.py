from datetime import datetime


event_history = []


def record_event(event_type, description, panel_code=None):
    event = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "event_type": event_type,
        "description": description,
        "panel_code": panel_code
    }

    event_history.append(event)

    return {
        "success": True,
        "event": event,
        "source": "Event Log"
    }


def escalate_to_supervisor(reason, panel_code=None):
    event = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "event_type": "ESCALATION",
        "description": reason,
        "panel_code": panel_code
    }

    event_history.append(event)

    return {
        "success": True,
        "escalated": True,
        "reason": reason,
        "event": event,
        "source": "Supervisor Escalation"
    }


def get_history():
    return event_history