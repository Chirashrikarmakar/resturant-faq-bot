from flask import Flask, render_template_string, request, jsonify
import json
import os

app = Flask(__name__)

# Load FAQs and menu
with open("faqs.json", "r") as f:
    data = json.load(f)

faqs = data["faqs"]

# HTML + CSS (WhatsApp-style chat)
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Restaurant FAQ Bot</title>
    <style>
        body { font-family: Arial; background:#f5f5f5; margin:0; padding:0; }
        .header { text-align:center; background:#8B4513; color:#fff; padding:20px; }
        .header h1 { margin:0; font-size:40px; }
        .header h2 { margin:5px 0; font-size:28px; font-weight:normal; }
        .header h3 { margin:0; font-size:20px; font-weight:normal; }
        .chat-container { max-width:600px; margin:20px auto; background:#fff; border-radius:10px; padding:20px; box-shadow:0 0 10px rgba(0,0,0,0.1);}
        .message { padding:10px 15px; border-radius:20px; margin:5px 0; max-width:80%; clear:both; }
        .user { background:#007BFF; color:#fff; float:right; text-align:right; }
        .bot { background:#eee; color:#333; float:left; text-align:left; }
        input { width:70%; padding:10px; border-radius:20px; border:1px solid #ccc; }
        button { padding:10px 15px; border:none; border-radius:20px; background:#8B4513; color:#fff; cursor:pointer; margin-left:5px; }
        button:hover { background:#A0522D; }
        .quick-buttons { text-align:center; margin:10px 0; }
        .menu-item { font-weight:bold; margin:5px 0; }
        .veg { color:green; }
        .nonveg { color:red; }
        .dessert-drink { color:#8B4513; }
        .clearfix { clear:both; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Welcome</h1>
        <h2>Hummus Kitchen</h2>
        <h3>Your friendly partner</h3>
    </div>
    <div class="chat-container">
        <div id="chat"></div>
        <input id="userInput" placeholder="Type your question..." />
        <button onclick="send()">Send</button>
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
