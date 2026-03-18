from flask import Flask
from flask import render_template
app = Flask(__name__)


@app.route("/")
def home():
    return render_template("begin.html")

@app.route("/account")
def account():
    return render_template("account.html")

@app.route("/maakpost")
def maakpost():
    return render_template("maakpost.html")

@app.route("/inloggen")
def inloggen():
    return render_template("inloggen.html")

if __name__ == "__main__":
    app.run(debug=True)
