from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # <- Permite CORS para qualquer origem

BYTEZ_KEY = "82aeed12438e4526e91f4e00a70a5eba"

MODELS = {
    "chat": "https://api.bytez.com/models/v2/qwen/Qwen3-0.6B",
    "image": "https://api.bytez.com/models/v2/SG161222/RealVisXL_V5.0",
    "video": "https://api.bytez.com/models/v2/ali-vilab/text-to-video-ms-1.7b",
    "caption": "https://api.bytez.com/models/v2/nlpconnect/vit-gpt2-image-captioning"
}

@app.route("/api/run", methods=["POST"])
def run_vilor():
    try:
        data = request.get_json()
        mode = data.get("mode")
        prompt = data.get("input")

        if mode not in MODELS:
            return jsonify({"error": "Modo inválido"}), 400

        url = MODELS[mode]
        payload = {"messages": prompt} if mode=="chat" else {"text": prompt}

        headers = {
            "Authorization": BYTEZ_KEY,
            "Content-Type": "application/json"
        }

        resp = requests.post(url, json=payload, headers=headers)
        result = resp.json()

        if "error" in result:
            return jsonify({"error": result["error"]}), 400

        return jsonify({"output": result.get("output") or result.get("result")})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
