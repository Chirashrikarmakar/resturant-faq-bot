from flask import Flask, render_template_string, request, jsonify
import json
import os

app = Flask(__name__)

# Load FAQs and menu
with open("faqs.json", "r", encoding="utf-8") as f:
    data = json.load(f)

faqs = data["faqs"]

# HTML + CSS (WhatsApp-style chat)
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Restaurant FAQ Bot</title>
    <style>
        body { font-family: Arial, Helvetica, sans-serif; background:#f5f5f5; margin:0; padding:0; }
        .header { background:#8B4513; color:#fff; padding:14px 12px; }
        .header .brand { max-width:900px; margin:0 auto; display:flex; align-items:center; gap:12px; text-align:left; }
        .logo-svg { width:56px; height:56px; flex:0 0 56px; display:block; }
        .brand-text h1 { margin:0; font-size:18px; font-weight:700; line-height:1; }
        .brand-text h2 { margin:4px 0 0; font-size:16px; font-weight:700; }
        .brand-text h3 { margin:4px 0 0; font-size:12px; font-weight:400; opacity:0.95; color:#fff8f0; }

        .chat-container { max-width:420px; margin:18px auto; background:transparent; border-radius:12px; padding:0 12px 12px;}
        #chat { background:transparent; padding:12px; max-height:520px; overflow:auto; }

        .message { padding:12px 16px; border-radius:14px; margin:10px 0; max-width:78%; clear:both; position:relative; display:inline-block; }
        .user { background:#D2691E; color:#fff; float:right; text-align:right; }
        .user::after { content: 'User'; position:absolute; top:-18px; right:0; font-size:12px; color:#666; }

        .bot { background:#fff; color:#333; float:left; text-align:left; border-radius:12px; padding:14px; max-width:88%; box-shadow:0 6px 18px rgba(0,0,0,0.06); border:1px solid #f0f0f0; }

        /* Quick buttons styled as stacked card like the screenshot */
        .quick-buttons { display:block; margin:12px auto 0; max-width:100%; background:#fff; border-radius:12px; box-shadow:0 6px 16px rgba(0,0,0,0.06); overflow:hidden; border:1px solid #f0f0f0; }
        .quick-buttons button { display:block; width:100%; padding:12px 14px; border:0; background:transparent; text-align:left; color:#1a73e8; font-weight:600; cursor:pointer; border-top:1px solid #f3f3f3; }
        .quick-buttons button:first-child { border-top:0; }

        .chat-controls { display:flex; gap:8px; align-items:center; padding:10px 0; }
        #userInput { flex:1; padding:12px 14px; border-radius:30px; border:1px solid #e6e6e6; outline:none; }
        .send-btn { width:44px; height:44px; border-radius:50%; border:none; background:#8B4513; color:#fff; display:flex; align-items:center; justify-content:center; cursor:pointer; }
        .send-btn:hover { background:#A0522D; }

        .menu-item { font-weight:bold; margin:5px 0; }
        .veg { color:green; }
        .nonveg { color:red; }
        .dessert-drink { color:#8B4513; }
        .clearfix { clear:both; }
        /* Responsive adjustments */
        @media (max-width: 480px) {
            .header .brand { gap:10px; }
            .logo-svg { width:44px; height:44px; }
            .brand-text h1 { font-size:16px; }
            .brand-text h2 { font-size:14px; }
            .chat-container { max-width:100%; margin:12px; padding:0 10px 12px; }
            #chat { max-height:60vh; }
        }

        @media (min-width: 481px) and (max-width: 1024px) {
            .chat-container { max-width:720px; }
            .logo-svg { width:48px; height:48px; }
        }

        @media (min-width: 1025px) {
            .chat-container { max-width:900px; }
            .brand-text h1 { font-size:22px; }
            .brand-text h2 { font-size:18px; }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="brand">
            <svg class="logo-svg" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                <circle cx="32" cy="32" r="30" fill="#fff" />
                <rect x="14" y="22" width="36" height="22" rx="5" fill="#8B4513" />
                <circle cx="24" cy="32" r="3" fill="#fff" />
                <circle cx="40" cy="32" r="3" fill="#fff" />
                <rect x="26" y="38" width="12" height="4" rx="2" fill="#fff" />
                <!-- simple chef hat -->
                <path d="M20 18c2-6 12-8 24-2 0 0 6 6-6 8H26c-8 0-6-6-6-6z" fill="#fff" />
                <rect x="22" y="14" width="20" height="6" rx="3" fill="#fff" />
            </svg>
            <div class="brand-text">
                <h1>Welcome</h1>
                <h2>Hummus Kitchen</h2>
                <h3>Your friendly partner</h3>
            </div>
        </div>
    </div>
    <div class="chat-container">
        <div id="chat"></div>
        <div class="chat-controls">
            <input id="userInput" placeholder="Type your question..." />
            <button class="send-btn" onclick="send()">➤</button>
        </div>
        <div class="quick-buttons">
            <button onclick="sendQuick('Menu')">Menu</button>
            <button onclick="sendQuick('Vegetarian')">Vegetarian</button>
            <button onclick="sendQuick('Opening Hours')">Opening Hours</button>
            <button onclick="sendQuick('Location')">Location</button>
            <button onclick="sendQuick('Seating')">Seating</button>
            <button onclick="sendQuick('Home Delivery')">Home Delivery</button>
            <button onclick="sendQuick('Rooftop')">Rooftop</button>
        </div>
    </div>
<script>
function addMessage(text, sender) {
    let chat = document.getElementById("chat");
    let div = document.createElement("div");
    div.className = "message " + sender;
    div.innerHTML = text.replace(/\\n/g, "<br>");
    chat.appendChild(div);
    let clear = document.createElement("div");
    clear.className = "clearfix";
    chat.appendChild(clear);
    chat.scrollTop = chat.scrollHeight;
}

function send() {
    let q = document.getElementById("userInput").value;
    if(!q) return;
    addMessage(q, "user");
    fetch("/chat", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({"question": q})
    })
    .then(res => res.json())
    .then(data => addMessage(data.answer, "bot"));
    document.getElementById("userInput").value = "";
}

function sendQuick(text) {
    document.getElementById("userInput").value = text;
    send();
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

@app.route("/chat", methods=["POST"])
def chat():
    user_q = request.json.get("question", "").lower()

    # Check for "thank you" or greetings first
    if any(word in user_q for word in ["thank", "thanks"]):
        return jsonify({"answer":"You're welcome! Have a nice day 😊"})
    elif any(word in user_q for word in ["hi","hello","hey"]):
        return jsonify({"answer":"Hello! How can I help you today?"})

    # Check FAQs
    for faq in faqs:
        for keyword in faq.get("keywords", []):
            if keyword.lower() in user_q:
                answer = faq["answer"].replace("\n","<br>")
                return jsonify({"answer": answer})

    # Default reply
    return jsonify({"answer":"Sorry, I can help with menu, timings, location, and seating."})

# Deploy-ready for Render
if __name__=="__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
