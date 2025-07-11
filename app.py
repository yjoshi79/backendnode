from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import traceback

app = Flask(__name__)
CORS(app)

@app.route('/api/generate-itinerary', methods=['POST'])
def generate_itinerary():
    data = request.json
    destination = data.get('destination', '')
    days = data.get('days', '')
    budget = data.get('budget', '')
    companions = data.get('companions', '')

    prompt = (
        f"Create a detailed travel itinerary for {days} days in {destination} "
        f"for a {budget} budget, traveling with {companions}."
    )

    try:
        HF_TOKEN = os.getenv("HF_TOKEN")
        headers = {
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "application/json"
        }

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 600,
                "temperature": 0.7
            }
        }

        res = requests.post(
            "https://api-inference.huggingface.co/models/google/flan-ul2",
            headers=headers,
            json=payload
        )

        # ✅ Check response before parsing JSON
        if res.status_code != 200:
            print("HuggingFace API error:", res.status_code)
            print("Response text:", res.text)
            return jsonify({"itinerary": "Error from Hugging Face API"}), 500

        print("Raw HF response text:", res.text)  # Debugging line
        print("HF STATUS CODE:", res.status_code)
        print("HF RAW RESPONSE:", res.text)
        output = res.json()

        if isinstance(output, list):
            text = output[0].get("generated_text", "No response")
        elif isinstance(output, dict):
            text = output.get("generated_text", "No response")
        else:
            text = "Unexpected response format"

        return jsonify({"itinerary": text}), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"itinerary": "Error generating itinerary"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
