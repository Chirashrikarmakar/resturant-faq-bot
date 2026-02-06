from flask import Flask, render_template_string, request, jsonify
import json
import os

app = Flask(__name__)

# Safe path to faqs.json
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
faqs_path = os.path.join(BASE_DIR, "faqs.json")

# Load FAQs
with open(faqs_path, "r") as f:
    data = json.load(f)

faqs = data["faqs"]

# HTML page with buttons
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Restaurant FAQ Bot</title>
    <style>
        body { font-family: Arial; text-align:center; padding:20px; background:#f5f5f5; }
        input { padding:8px; width:200px; }
        button { padding:8px 12px; margin:5px; border:none; border-radius:5px; background:#007BFF; color:white; cursor:pointer; }
        button:hover { background:#0056b3; }
        #response { margin-top: 20px; white-space: pre-line; font-size: 16px; }
    </style>
</head>
<body>
    <h2>Restaurant FAQ Bot</h2>

    <input id="userInput" placeholder="Ask a question..." />
    <button onclick="send()">Send</button>

    <p id="response"></p>

    <div>
        <button onclick="sendQuick('Menu')">Menu</button>
        <button onclick="sendQuick('Opening Hours')">Opening Hours</button>
        <button onclick="sendQuick('Location')">Location</button>
        <button onclick="sendQuick('Seating')">Seating</button>
        <button onclick="sendQuick('Vegetarian Options')">Vegetarian Options</button>
        <button onclick="sendQuick('Rooftop')">Rooftop</button>
        <button onclick="sendQuick('Home Delivery')">Home Delivery</button>
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


# Homepage route
@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_PAGE)

# Chat route
@app.route("/chat", methods=["POST"])
def chat():
    user_q = request.json.get("question", "").lower()

    for faq in faqs:
        for keyword in faq.get("keywords", []):
            if keyword.lower() in user_q:
                return jsonify({"answer": faq["answer"]})

    return jsonify({"answer": "Sorry, I can help with menu, timings, location, and seating."})

if __name__ == "__main__":
    app.run(debug=True)
