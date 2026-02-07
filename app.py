from flask import Flask, render_template_string, request, jsonify
import json
import os

app = Flask(__name__)

# Load FAQs and menu
with open("faqs.json", "r", encoding="utf-8") as f:
    data = json.load(f)

faqs = data["faqs"]

# Commercial styled HTML + CSS
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Restaurant FAQ Bot</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        body { font-family: Inter, Arial, Helvetica, sans-serif; background: linear-gradient(180deg,#f3f6fb 0%, #ffffff 100%); margin:0; padding:0; -webkit-font-smoothing:antialiased; }
        .header { background:#8B4513; color:#fff; padding:14px 12px; }
        .header .brand { max-width:1100px; margin:0 auto; display:flex; align-items:center; gap:12px; text-align:left; }
        .logo-svg { width:56px; height:56px; flex:0 0 56px; display:block; border-radius:10px; box-shadow:0 6px 18px rgba(139,69,19,0.18); }
        .brand-text h1 { margin:0; font-size:18px; font-weight:700; line-height:1; }
        .brand-text h2 { margin:4px 0 0; font-size:16px; font-weight:700; }
        .brand-text h3 { margin:6px 0 0; font-size:12px; font-weight:400; opacity:0.95; color:#fffbe9; }

        .chat-container { max-width:420px; margin:20px auto; background:transparent; border-radius:14px; padding:0 12px 12px;}
        /* central chat card */
        .chat-card { background:#fff; border-radius:16px; box-shadow:0 20px 40px rgba(2,6,23,0.08); overflow:hidden; border:1px solid rgba(10,10,10,0.03); }
        #chat { background:transparent; padding:18px; max-height:520px; overflow:auto; }

        .chat-header { display:flex; align-items:center; gap:12px; padding:14px 18px; background:linear-gradient(90deg, rgba(139,69,19,0.98) 0%, rgba(138,93,61,0.95) 100%); color:#fff; }
        .chat-header .avatar { width:44px; height:44px; border-radius:50%; background:#fff; display:flex; align-items:center; justify-content:center; box-shadow:0 6px 18px rgba(0,0,0,0.12); flex:0 0 44px; }
        .chat-header .title { font-weight:700; font-size:16px; }
        .chat-header .status { font-size:12px; opacity:0.9; margin-top:2px; }
        .chat-header .spacer { flex:1; }
        .chat-header .close-btn { background:transparent; border:0; color:#fff; font-size:18px; cursor:pointer; opacity:0.95; }

        .message { padding:12px 16px; border-radius:14px; margin:10px 0; max-width:78%; clear:both; position:relative; display:inline-block; font-size:15px; line-height:1.4; }
        .user { background:#D2691E; color:#fff; float:right; text-align:right; box-shadow:0 8px 18px rgba(210,105,30,0.18); border-bottom-right-radius:4px; }
        .user .pill { display:inline-block; padding:6px 10px; border-radius:14px; }

        .bot { background:#fbfbfd; color:#18212b; float:left; text-align:left; border-radius:12px; padding:14px; max-width:88%; box-shadow:0 8px 22px rgba(6,22,33,0.06); border:1px solid #f1f3f6; }
        .bot .bubble { display:block; }

        .chat-controls { display:flex; gap:8px; align-items:center; padding:14px; background:transparent; }
        #userInput { flex:1; padding:12px 14px; border-radius:26px; border:1px solid #e6e9ee; outline:none; background:#fff; box-shadow:0 6px 18px rgba(2,6,23,0.04); }
        .send-btn { width:48px; height:48px; border-radius:50%; border:none; background:#0b66ff; color:#fff; display:flex; align-items:center; justify-content:center; cursor:pointer; box-shadow:0 10px 24px rgba(11,102,255,0.14); }
        .send-btn:hover { transform:translateY(-1px); }

        .menu-item { font-weight:700; margin:5px 0; }
        .veg { color:green; }
        .nonveg { color:red; }
        .dessert-drink { color:#8B4513; }
        .clearfix { clear:both; }
        /* Responsive adjustments */
        @media (max-width: 480px) {
            .header .brand { gap:10px; padding-right:8px; }
            .logo-svg { width:44px; height:44px; }
            .brand-text h1 { font-size:16px; }
            .brand-text h2 { font-size:14px; }
            .brand-text h3 { font-size:12px; }
            .chat-container { max-width:100%; margin:8px; padding:0 6px 0; }
            /* Give chat area room for fixed input controls */
            #chat { max-height:calc(100vh - 180px); padding-bottom:140px; }
            .message { font-size:15px; margin:10px 0; }

            /* Make controls sticky at bottom on small screens */
            .chat-controls { position:fixed; left:8px; right:8px; bottom:12px; padding:8px; background:transparent; z-index:40; }
            .chat-controls > #userInput { border-radius:28px; padding:12px 14px; font-size:15px; }
            .send-btn { width:48px; height:48px; border-radius:50%; }

            /* Avoid the page content being hidden under fixed controls */
            body { padding-bottom:180px; }
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
            <div class="chat-card">
                <div class="chat-header">
                    <div class="avatar" aria-hidden="true">
                        <svg width="28" height="28" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
                            <circle cx="32" cy="32" r="30" fill="#fff" />
                            <rect x="18" y="26" width="28" height="18" rx="5" fill="#8B4513" />
                            <circle cx="26" cy="35" r="2.5" fill="#fff" />
                            <circle cx="38" cy="35" r="2.5" fill="#fff" />
                            <path d="M24 22c2-5 10-6 20-2 0 0 4 4-4 6H28c-6 0-4-4-4-4z" fill="#fff" />
                        </svg>
                    </div>
                    <div>
                        <div class="title">Restaurant ChatBot</div>
                        <div class="status">Online</div>
                    </div>
                    <div class="spacer"></div>
                    <button class="close-btn" aria-label="close">✕</button>
                </div>
                <div id="chat"></div>
                <div class="chat-controls">
                    <input id="userInput" placeholder="Type your question..." autocomplete="off" />
                    <button class="send-btn" onclick="send()">➤</button>
                </div>
                <!-- Quick-action buttons intentionally removed -->
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
