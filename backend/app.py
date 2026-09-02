from flask import Flask, jsonify, request
from flask_cors import CORS

from agent import run_agent
from tools import get_panel, get_history

app = Flask(__name__)
CORS(app)


@app.route("/api/agent", methods=["POST"])
def agent():
    try:
        data = request.get_json()

        user_message = data.get("message", "")
        workstation_id = data.get("workstation_id")
        panel_code = data.get("panel_code")

        result = run_agent(
            user_message=user_message,
            workstation_id=workstation_id,
            panel_code=panel_code
        )

        return jsonify({
            "success": True,
            **result
        })

    except Exception as error:
        print("AGENT ERROR:", repr(error))

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500
    
@app.route("/api/panels/<panel_code>", methods=["GET"])
def panel(panel_code):
    result = get_panel(panel_code)

    if not result["found"]:
        return jsonify(result), 404

    return jsonify(result)

@app.route("/api/test", methods=["GET"])
def test():
    return jsonify({
        "success": True,
        "message": "Flask is working"
    })

if __name__ == "__main__":
    app.run(debug=True)