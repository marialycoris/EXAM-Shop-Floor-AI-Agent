import json
import os


def get_panel(panel_code):
    file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data",
        "panels.json"
    )

    with open(file_path, "r") as file:
        panels = json.load(file)

    for panel in panels:
        if panel["panel_code"] == panel_code:
            return {
                "found": True,
                "panel": panel,
                "source": f"Panel {panel_code}"
            }

    return {
        "found": False,
        "panel": None,
        "source": f"Panel {panel_code}"
    }