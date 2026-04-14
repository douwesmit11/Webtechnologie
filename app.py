from flask import Flask, request, redirect, jsonify
from flask import session
from flask import render_template
from models import db, User
from werkzeug.security import generate_password_hash
from datetime import datetime
import re
import os
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"

db.init_app(app)
app.secret_key = "geheim"


@app.route("/")
def home():
    return render_template("pages/begin.html")






@app.route("/account")
def account():
    return render_template("pages/account.html")


@app.route("/maakpost")
def maakpost():
    return render_template("pages/maakpost.html")


@app.route("/inloggen")
def inloggen():
    return render_template("pages/inloggen.html")


@app.route("/registreren")
def regristreren():
    print(type(datetime.now()))

    return render_template("pages/registreren.html")

@app.route("/registreren/create", methods=["POST"])
def createUser():
    data = request.form

    username = data.get('username')
    email = data.get('email')
    password = data.get('password_repeat')

    timestamp = int(datetime.now().timestamp())

    if not username or len(username) < 3:
        return 
        return jsonify({"error": "Gebruikersnaam moet minimaal 3 karakters bevatten"}), 400

    if not re.match(EMAIL_REGEX, email):
        return jsonify({"error": "Ongeldige email"}), 400

    if not password or len(password) < 6:
        return jsonify({"error": "Wachtwoord moet minimaal 6 karakters bevatten"}), 400

    # Check duplicates
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email is al in gebruik"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Gebruikersnaam is al in gebruik"}), 400

    
    hashed_password = generate_password_hash(password)

    # Create user
    new_user = User(
        username=username,
        email=email,
        password=hashed_password,
        created_at=timestamp,
        updated_at=timestamp
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "User succesvol geregistreerd"
    }), 201


@app.route("/users")
def get_users():
    users = User.query.all()

    result = []
    for user in users:
        result.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": str(user.created_at)
        })

    return result

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
