import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

from dotenv import load_dotenv

load_dotenv() # Load variables from .env

# 🪄 Loaded from .env file
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Using a standard model with the new router
API_URL = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-cnn"
HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

BUGS_FILE = "bugs.json"

def load_bugs():
    if not os.path.exists(BUGS_FILE):
        return []
    try:
        with open(BUGS_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except (json.JSONDecodeError, Exception):
        return []

def save_bugs(bugs):
    with open(BUGS_FILE, "w") as f:
        json.dump(bugs, f, indent=4)

@app.route("/bugs", methods=["GET"])
def get_bugs():
    return jsonify(load_bugs())

@app.route("/bugs", methods=["POST"])
def add_bug():
    try:
        data = request.get_json()
        title = data.get("title", "")
        description = data.get("description", "")

        if not title or not description:
            return jsonify({"error": "Title and description are required"}), 400

        # --- Call Hugging Face for summary ---
        summary = "No summary generated."
        try:
            payload = {"inputs": description}
            response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=20)
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    summary = result[0].get("summary_text", summary)
            elif response.status_code == 401:
                summary = "HuggingFace API Key invalid or not provided."
            else:
                summary = f"HuggingFace error: {response.status_code}"
        except Exception as e:
            summary = f"Could not generate summary: {str(e)}."

        bug_entry = {
            "id": len(load_bugs()) + 1,
            "title": title,
            "description": description,
            "summary": summary,
            "status": "Open"
        }

        bugs = load_bugs()
        bugs.append(bug_entry)
        save_bugs(bugs)

        return jsonify({
            "message": "Bug submitted successfully!",
            "bug": bug_entry
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
