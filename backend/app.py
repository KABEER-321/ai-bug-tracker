from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

# 🪄 Replace with your Hugging Face API key
HUGGINGFACE_API_KEY = "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"

API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}


@app.route("/bugs", methods=["POST"])
def add_bug():
    try:
        data = request.get_json()
        title = data.get("title", "")
        description = data.get("description", "")

        # --- Call Hugging Face for summary ---
        summary = "Fallback summary: " + description
        try:
            payload = {"inputs": description}
            response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=20)
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    summary = result[0].get("summary_text", summary)
            else:
                summary = f"HuggingFace error: {response.text}"
        except Exception as e:
            summary = f"Could not generate summary via Hugging Face: {str(e)}. Using fallback."

        bug_entry = {
            "title": title,
            "description": description,
            "summary": summary
        }

        with open("bugs.json", "a") as f:
            f.write(json.dumps(bug_entry) + "\n")

        return jsonify({
            "message": "Bug submitted successfully!",
            "summary": summary
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=False)
