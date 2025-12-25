import requests
import json
import sys

try:
    response = requests.post(
        "http://127.0.0.1:5000/bugs",
        json={
            "title": "Button not working",
            "description": "The submit button does nothing when clicked. No errors in console."
        },
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        summary = data.get("bug", {}).get("summary", "")
        with open("debug_output.txt", "w") as f:
            f.write(summary)
        print("Written to debug_output.txt")
        sys.exit(0)
    else:
        print(f"FAILED: {response.status_code}")
        print(response.text)
        sys.exit(1)
except Exception as e:
    print(f"ERROR: {str(e)}")
    sys.exit(1)
