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
</head>
<body>
    <h2>Restaurant FAQ Bot</h2>
    <input id="userInput" placeholder="Ask a question..." />
    <button onclick="send()">Send</button>
    <p id="response"></p>

<script>
function send(){
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
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

@app.route("/chat", methods=["POST"])
def chat():
    user_q = request.json["question"].lower()

    for faq in faqs:
        if faq["question"].lower() in user_q:
            return jsonify({"answer": faq["answer"]})

    return jsonify({"answer": "Sorry, I can help with menu, timings, location, and seating."})

if __name__ == "__main__":
    app.run(debug=True)
