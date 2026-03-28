from flask import Flask, request, redirect
from flask import session
from flask import render_template
from models import db, User
import os
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.secret_key = "geheim"

@app.route("/")
def home():
    return render_template("begin.html")
def vorige():
    ...


def volgende():
    ...


@app.route("/account.html")
def account():
    return render_template("account.html")

@app.route("/maakpost.html")
def maakpost():
    return render_template("maakpost.html")

@app.route("/inloggen.html")
def inloggen():
    return render_template("inloggen.html")

@app.route("/regristreren.html", methods=["GET", "POST"])
def regristreren():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        return redirect("/inloggen.html")

    return render_template("regristreren.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
