from flask import Flask, request, jsonify, render_template_string
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

# Rota principal com frontend
@app.route("/")
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Vilor AI</title>
<style>
    body { font-family: Arial, sans-serif; background: #f5f5f5; margin: 0; padding: 0; }
    .container { max-width: 800px; margin: 50px auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
    h1 { text-align: center; }
    select, input[type="text"], button { padding: 10px; margin: 5px 0; width: 100%; box-sizing: border-box; }
    .chat-box { border: 1px solid #ddd; padding: 10px; height: 300px; overflow-y: auto; margin-top: 10px; background: #fafafa; border-radius: 5px; }
    .message { margin: 5px 0; }
    .user { color: blue; }
    .bot { color: green; }
</style>
</head>
<body>
<div class="container">
    <h1>Vilor AI</h1>
    <select id="mode">
        <option value="chat">Chat</option>
        <option value="image">Imagem</option>
        <option value="video">Vídeo</option>
        <option value="caption">Legenda de Imagem</option>
    </select>
    <input type="text" id="input" placeholder="Digite sua mensagem...">
    <button onclick="sendMessage()">Enviar</button>
    <div class="chat-box" id="chatBox"></div>
</div>

<script>
function appendMessage(sender, text) {
    const chatBox = document.getElementById('chatBox');
    const msg = document.createElement('div');
    msg.className = 'message ' + sender;
    msg.textContent = (sender === 'user' ? 'Você: ' : 'Bytez: ') + text;
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage() {
    const mode = document.getElementById('mode').value;
    const input = document.getElementById('input').value;
    if (!input) return;
    
    appendMessage('user', input);
    document.getElementById('input').value = '';

    try {
        const res = await fetch('/api/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode: mode, input: input })
        });
        const data = await res.json();
        if (data.error) {
            appendMessage('bot', 'Erro: ' + data.error);
        } else {
            appendMessage('bot', data.output || 'Sem resposta');
        }
    } catch (err) {
        appendMessage('bot', 'Erro na comunicação: ' + err.message);
    }
}
</script>
</body>
</html>
    """)

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
