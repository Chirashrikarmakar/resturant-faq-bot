from flask import Flask, request, jsonify, render_template_string
import json

app = Flask(__name__)

# Load FAQs
with open("faqs.json", "r") as f:
    data = json.load(f)

faqs = data["faqs"]

# Simple home page
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
        document.getElementById("response").innerText = data.answer;
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


@app.route("/chat", methods=["POST"])
def chat():
    user_q = request.json["question"].lower()

    for faq in faqs:
        faq_question = faq["question"].lower()
        # Simple substring match
        if faq_question in user_q or user_q in faq_question:
            return jsonify({"answer": faq["answer"]})

    return jsonify({"answer": "Sorry, I can help with menu, timings, location, and seating."})


if __name__ == "__main__":
    app.run(debug=True)
