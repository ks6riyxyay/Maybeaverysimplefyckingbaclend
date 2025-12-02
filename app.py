from flask import Flask, request, jsonify, render_template_string
import requests
import base64

app = Flask(__name__)

# Endpoint público do modelo OVI no Hugging Face
OVI_MODEL_URL = "https://huggingface.co/open-video/ovi-1.0/resolve/main"  # modelo público

# ---------------- Frontend ----------------
@app.route("/")
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>VilorAI - Text2Video</title>
<style>
body { font-family: Arial,sans-serif; background:#f5f5f5; margin:0; padding:0;}
.container { max-width:800px; margin:50px auto; background:white; padding:20px; border-radius:10px; box-shadow:0 0 10px rgba(0,0,0,0.1);}
h1 { text-align:center; }
.chat-box { display:flex; flex-direction:column; gap:10px; height:500px; overflow-y:auto; border:1px solid #ddd; padding:10px; border-radius:5px; background:#fafafa;}
.message { padding:8px 12px; border-radius:12px; max-width:75%; }
.user { background:#d0e7ff; color:#003366; align-self:flex-end;}
.bot { background:#e0ffe0; color:#006600; align-self:flex-start;}
input[type=text] { width:75%; padding:10px; border-radius:5px; border:1px solid #ccc;}
button { padding:10px 20px; border:none; background:#4CAF50; color:white; border-radius:5px; cursor:pointer;}
button:hover { background:#45a049; }
video { width:100%; border-radius:8px; margin-top:10px; }
</style>
</head>
<body>
<div class="container">
<h1>VilorAI - Text2Video</h1>
<div style="display:flex; gap:10px; margin-bottom:10px;">
<input type="text" id="input" placeholder="Digite seu prompt...">
<button onclick="sendMessage()">Enviar</button>
</div>
<div class="chat-box" id="chatBox"></div>
</div>

<script>
function appendMessage(sender, text, isVideo=false){
    const chatBox = document.getElementById('chatBox');
    const msgWrapper = document.createElement('div');
    msgWrapper.className = 'message ' + sender;
    if(isVideo){
        const video = document.createElement('video');
        video.src = text;
        video.controls = true;
        video.autoplay = false;
        video.loop = false;
        video.style.width='100%';
        msgWrapper.appendChild(video);
    } else {
        msgWrapper.textContent = text;
    }
    chatBox.appendChild(msgWrapper);
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage(){
    const input = document.getElementById('input').value.trim();
    if(!input) return;
    appendMessage('user', input);
    document.getElementById('input').value='';

    try{
        const res = await fetch('/api/text2video', {
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({prompt:input})
        });
        const data = await res.json();
        if(data.error){
            appendMessage('bot', 'Erro: '+data.error);
        } else {
            appendMessage('bot', data.video_url, true);
        }
    }catch(err){
        appendMessage('bot','Erro de comunicação: '+err.message);
    }
}
</script>
</body>
</html>
""")

# ---------------- Backend ----------------
@app.route("/api/text2video", methods=["POST"])
def text2video():
    data = request.get_json()
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"error":"Prompt vazio"}),400

    try:
        # Chamada HTTP para Hugging Face Model Hub (public)
        # Usando curl-like request via Python
        payload = {"inputs": prompt}
        headers = {"Content-Type":"application/json"}
        # Aqui usamos endpoint público sem token
        resp = requests.post(
            "https://api-inference.huggingface.co/models/open-video/ovi-1.0",
            headers=headers,
            json=payload,
            timeout=300
        )
        if resp.status_code != 200:
            return jsonify({"error":f"Status {resp.status_code}: {resp.text}"}),500

        # O modelo retorna vídeo em base64
        result = resp.json()
        if "video" not in result:
            return jsonify({"error":"Resposta inesperada do modelo"}),500

        video_bytes = base64.b64decode(result["video"])
        filename = "static/video.mp4"
        with open(filename,"wb") as f:
            f.write(video_bytes)

        return jsonify({"video_url":"/"+filename})
    except Exception as e:
        return jsonify({"error":str(e)}),500

# ---------------- Run Server ----------------
if __name__=="__main__":
    app.run(host="0.0.0.0", port=8080)
