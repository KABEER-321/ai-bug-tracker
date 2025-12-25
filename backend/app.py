import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

from dotenv import load_dotenv

load_dotenv() # Load variables from .env

import google.generativeai as genai

# 🪄 Loaded from .env file
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

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

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "AI Bug Tracker API is running!", "endpoints": ["/bugs"]})

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

        # --- Call Gemini for Solution ---
        solution = "No solution found."
        try:
            prompt = f"""
            You are a highly skilled software developer. 
            Provide a clear, step-by-step technical solution to fix the following bug.
            
            Bug Title: {title}
            Description: {description}
            
            Format the solution as a numbered list of steps. Keep it concise/actionable.
            """
            response = model.generate_content(prompt)
            solution = response.text
        except Exception as e:
            solution = f"Could not generate solution: {str(e)}."

        bug_entry = {
            "id": len(load_bugs()) + 1,
            "title": title,
            "description": description,
            "summary": solution, # Keeping the key 'summary' for DB compatibility
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
