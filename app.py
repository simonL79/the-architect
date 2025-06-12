from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/api/execute", methods=["POST"])
def execute():
    data = request.get_json()
    return jsonify({
        "status": "online",
        "message": f"Command '{data.get('command')}' received"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
