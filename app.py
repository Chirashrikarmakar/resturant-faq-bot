from flask import Flask, render_template_string, request, jsonify
import json, os

app = Flask(__name__)

# Load FAQs
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
faqs_file = os.path.join(BASE_DIR, "faqs.json")

with open(faqs_file, "r", encoding="utf-8") as f:
    data = json.load(f)

faqs = data["faqs"]

# HTML page with chocolate brown theme
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Restaurant FAQ Bot</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            background: #f2f2f2;
            display: flex;
            justify-content: center;
            padding: 20px;
        }
        #container {
            width: 700px;
            background: #fff;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        h2 {
            text-align:center;
            color:#7B3F00; /* Chocolate Brown */
            margin-bottom: 20px;
        }
        #inputContainer {
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
        }
        #userInput {
            flex: 1;
            padding: 12px;
            font-size: 16px;
            border: 1px solid #ccc;
            border-radius: 8px 0 0 8px;
        }
        #sendBtn {
            padding: 12px 20px;
            background: #7B3F00;
            color: white;
            border: none;
            border-radius: 0 8px 8px 0;
            cursor: pointer;
            font-weight: 500;
        }
        #sendBtn:hover {
            background: #5C2D00;
        }
        #buttons {
            text-align:center;
            margin-bottom: 20px;
        }
        .quick-btn {
            margin:5px 3px;
            padding:10px 15px;
            border:none;
            border-radius: 6px;
            background:#7B3F00;
            color:white;
            cursor:pointer;
            font-weight:500;
            transition: 0.3s;
        }
        .quick-btn:hover {
            background:#5C2D00;
        }
        #response {
            max-height: 450px;
            overflow-y: auto;
            padding: 10px;
        }
        .category {
            background: #7B3F00;
            color: #fff;
            padding: 8px 12px;
            border-radius: 6px;
            font-weight: bold;
            margin-top: 15px;
        }
        .item-card {
            background: #f9f9f9;
            padding: 10px 12px;
            border-radius: 8px;
            margin: 6px 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
    </style>
</head>
<body>
    <div id="container">
        <h2>Restaurant FAQ Bot</h2>
        <div id="inputContainer">
            <input id="userInput" placeholder="Ask a question..." />
            <button id="sendBtn" onclick="send()">Send</button>
        </div>

        <div id="buttons">
            <button class="quick-btn" onclick="sendQuick('Menu')">Menu</button>
            <button class="quick-btn" onclick="sendQuick('Opening Hours')">Opening Hours</button>
            <button class="quick-btn" onclick="sendQuick('Location')">Location</button>
            <button class="quick-btn" onclick="sendQuick('Seating')">Seating</button>
            <button class="quick-btn" onclick="sendQuick('Vegetarian Options')">Vegetarian Options</button>
            <button class="quick-btn" onclick="sendQuick('Rooftop')">Rooftop</button>
            <button class="quick-btn" onclick="sendQuick('Home Delivery')">Home Delivery</button>
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
        let text = data.answer;

        // Format Menu nicely
        if(q.toLowerCase().includes("menu")) {
            text = text.split("\\n").map(line => {
                if(line.endsWith(":")) return '<div class="category">'+line+'</div>';
                return '<div class="item-card">'+line+'</div>';
            }).join('');
        } else {
            text = text.replace(/\\n/g, "<br>");
        }

        document.getElementById("response").innerHTML = text;
        document.getElementById("response").scrollTop = 0;
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
                return jsonify({"answer": faq["answer"]})
    return jsonify({"answer": "Sorry, I can help with menu, timings, location, and seating."})

if __name__ == "__main__":
    app.run(debug=True)
