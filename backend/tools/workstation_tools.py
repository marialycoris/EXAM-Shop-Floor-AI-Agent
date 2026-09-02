import json
import os


def get_workstation_requirements(workstation_id):
    file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data",
        "workstations.json"
    )

    with open(file_path, "r") as file:
        workstations = json.load(file)

    for workstation in workstations:
        if workstation["workstation_id"] == workstation_id:
            return {
                "found": True,
                "workstation": workstation,
                "source": f"Workstation {workstation_id}"
            }

    return {
        "found": False,
        "workstation": None,
        "source": f"Workstation {workstation_id}"
    }