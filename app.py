from flask import Flask, render_template_string, request, jsonify
import json, os

app = Flask(__name__)

# Load FAQs
with open("faqs.json", "r", encoding="utf-8") as f:
    faqs = json.load(f)["faqs"]

# Veg / Non-Veg items for menu coloring
VEG_ITEMS = ["Bruschetta","Garlic Bread","Soup of the Day","Caesar Salad","Greek Salad","Garden Salad","Margherita Pizza","Veggie Burger","Chocolate Lava Cake","Tiramisu","Ice Cream Sundae","Fresh Juice","Soft Drinks","Coffee","Tea"]
NON_VEG_ITEMS = ["Spaghetti Bolognese","Grilled Chicken"]

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Hummus Kitchen FAQ Bot</title>
    <style>
        body { font-family:Arial,sans-serif; background:#f2f2f2; padding:20px; }
        #container { width:700px; margin:0 auto; background:#fff; border-radius:12px; padding:25px; box-shadow:0 5px 20px rgba(0,0,0,0.1); }
        .welcome-header { color:#7B3F00; text-align:center; margin-bottom:25px; }
        .welcome-header h1 { font-size:36px; margin:0; }
        .welcome-header h2 { font-size:28px; margin:0; }
        .welcome-header h3 { font-size:20px; margin:0; }

        input { padding:12px; width:70%; font-size:16px; border-radius:8px 0 0 8px; border:1px solid #ccc; }
        button.send-btn { padding:12px 20px; border:none; background:#7B3F00; color:white; border-radius:0 8px 8px 0; cursor:pointer; }
        button.send-btn:hover { background:#5C2D00; }
        #buttons { text-align:center; margin:15px 0; }
        .quick-btn { margin:5px 3px; padding:10px 15px; border:none; border-radius:6px; background:#7B3F00; color:white; cursor:pointer; }
        .quick-btn:hover { background:#5C2D00; }
        #response { text-align:left; max-height:500px; overflow-y:auto; padding:10px; border:1px solid #ccc; border-radius:8px; background:#fafafa; }

        .category { background:#7B3F00; color:#fff; padding:6px 10px; border-radius:6px; font-weight:bold; margin-top:15px; font-size:18px; }
        .item-card { padding:6px 10px; border-radius:6px; margin:4px 0; }
        .veg { color:green; }
        .nonveg { color:red; }
        .dessert-drink { color:#7B3F00; }
    </style>
</head>
<body>
<div id="container">
    <div class="welcome-header">
        <h1>Welcome</h1>
        <h2>Hummus Kitchen</h2>
        <h3>Your own partner</h3>
    </div>

    <div>
        <input id="userInput" placeholder="Ask a question..." />
        <button class="send-btn" onclick="send()">Send</button>
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
const VEG_ITEMS = ["Bruschetta","Garlic Bread","Soup of the Day","Caesar Salad","Greek Salad","Garden Salad","Margherita Pizza","Veggie Burger","Chocolate Lava Cake","Tiramisu","Ice Cream Sundae","Fresh Juice","Soft Drinks","Coffee","Tea"];
const NON_VEG_ITEMS = ["Spaghetti Bolognese","Grilled Chicken"];

function sendQuick(text){
    document.getElementById("userInput").value=text;
    send();
}

function send(){
    const q = document.getElementById("userInput").value;
    fetch("/chat", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify({question:q})
    }).then(res=>res.json())
      .then(data=>{
          let text = data.answer;

          // Format menu
          if(q.toLowerCase().includes("menu")){
              text = text.split("\\n").map(line=>{
                  line=line.trim();
                  if(line.endsWith(":")) return '<div class="category">'+line+'</div>';
                  else if(line.startsWith("- ")){
                      const itemText = line.substring(2);
                      const itemName = itemText.split(" - ")[0].trim();
                      if(VEG_ITEMS.includes(itemName)) return '<div class="item-card veg">'+itemText+'</div>';
                      else if(NON_VEG_ITEMS.includes(itemName)) return '<div class="item-card nonveg">'+itemText+'</div>';
                      else return '<div class="item-card dessert-drink">'+itemText+'</div>';
                  } else if(line.length>0) return '<div class="item-card dessert-drink">'+line+'</div>';
                  return '';
              }).join('');
          } else {
              text = text.replace(/\\n/g,"<br>");
          }

          document.getElementById("response").innerHTML = text;
          document.getElementById("response").scrollTop = 0;
      });
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
    user_q = request.json.get("question","").strip().lower()
    for faq in faqs:
        q_lower = faq["question"].lower()
        keywords = [k.lower() for k in faq.get("keywords",[])]
        if user_q == q_lower or user_q in keywords:
            return jsonify({"answer": faq["answer"]})
    # fallback menu
    if "menu" in user_q:
        for faq in faqs:
            if faq["question"].lower() == "menu":
                return jsonify({"answer": faq["answer"]})
    return jsonify({"answer":"Sorry, I can help with menu, timings, location, and seating."})

if __name__=="__main__":
    app.run(debug=True)
