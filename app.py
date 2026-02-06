from flask import Flask, render_template_string, request, jsonify
import json
import os

app = Flask(__name__)

# Load FAQs from the same folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
faqs_file = os.path.join(BASE_DIR, "faqs.json")

with open(faqs_file, "r", encoding="utf-8") as f:
    data = json.load(f)

faqs = data["faqs"]

# HTML page with fixed layout
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Restaurant FAQ Bot</title>
    <style>
        body { font-family: Arial; background:#f5f5f5; display:flex; justify-content:center; padding:20px; }
        #container { width: 600px; background:white; padding:20px; border-radius:10px; box-shadow:0 0 10px rgba(0,0,0,0.2); }
        h2 { text-align:center; }
        #userInput { padding:10px; width:70%; margin-right:5px; }
        button { padding:10px 15px; margin:5px; border:none; border-radius:5px; background:#007BFF; color:white; cursor:pointer; }
        button:hover { background:#0056b3; }
        #response { margin-top:20px; white-space: pre-line; font-size:16px; line-height:1.5; text-align:left; }
        #buttons { text-align:center; margin-top:10px; }
    </style>
</head>
<body>
    <div id="container">
        <h2>Restaurant FAQ Bot</h2>
        <div>
            <input id="userInput" placeholder="Ask a question..." />
            <button onclick="send()">Send</button>
        </div>
        <div id="buttons">
            <button onclick="sendQuick('Menu')">Menu</button>
            <button onclick="sendQuick('Opening Hours')">Opening Hours</button>
            <button onclick="sendQuick('Location')">Location</button>
            <button onclick="sendQuick('Seating')">Seating</button>
            <button onclick="sendQuick('Vegetarian Options')">Vegetarian Options</button>
            <button onclick="sendQuick('Rooftop')">Rooftop</button>
            <button onclick="sendQuick('Home Delivery')">Home Delivery</button>
        </div>
        <div id="response"></div>
    </div>

<script>
function send() {
    let q = document.getElementById("userInput").value;
    fetch("/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({"question": q})
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("response").innerHTML = data.answer;
    });
}

function sendQuick(text) {
    document.getElementById("userInput").value = text;
    send();
}
</script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_PAGE)

@app.route("/chat", methods=["POST"])
def chat():
    user_q = request.json.get("question", "").lower()
    for faq in faqs:
        for keyword in faq.get("keywords", []):
            if keyword.lower() in user_q:
                answer = faq["answer"].replace("\n", "<br>")
                return jsonify({"answer": answer})
    return jsonify({"answer": "Sorry, I can help with menu, timings, location, and seating."})

if __name__ == "__main__":
    app.run(debug=True)
