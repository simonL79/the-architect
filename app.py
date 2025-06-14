from flask import Flask, request, jsonify
from flask_cors import CORS
from ai_builder import run_gpt_command
from dotenv import load_dotenv
import os

# Load .flaskenv or production env
load_dotenv(dotenv_path=".flaskenv")

app = Flask(__name__)
CORS(app)

@app.route('/api/execute', methods=['POST'])
def execute_command():
    data = request.get_json()
    command = data.get("command", "")

    # ✅ Real GPT call — NOT a placeholder
    result = run_gpt_command(command)

    return jsonify({
        "response": result,
        "status": "gpt-online"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

