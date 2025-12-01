from flask import Flask, render_template, request
from transformers import pipeline

app = Flask(__name__)

# Load your model (same as your code)
gen = pipeline("text-generation", model="gpt2")

@app.route("/", methods=["GET", "POST"])
def home():
    output_text = ""

    if request.method == "POST":
        user_text = request.form["user_input"]  # Receive input from web form
        result = gen(user_text, max_new_tokens=500, do_sample=True, top_p=0.9, temperature=0.8)
        output_text = result[0]["generated_text"]

    return render_template("index.html", output=output_text)


if __name__ == "__main__":
    app.run(debug=True)
