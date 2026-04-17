from flask import Flask, request, redirect, flash
from flask import session, g
from flask import render_template, url_for
from models import db, User, NewsArticle
from datetime import timedelta
from werkzeug.utils import secure_filename
import uuid
import re
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=60)

UPLOAD_FOLDER = 'static/uploads/profile_images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db.init_app(app)
app.secret_key = "geheim"


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.before_request
def load_logged_in_user():
    g.user = None
    user_id = session.get("user_id")

    if user_id:
        g.user = User.query.get(user_id)


@app.context_processor
def inject_user():
    return dict(user=g.user)


@app.route("/")
def home():
    user = None
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()

    return render_template("pages/begin.html", user=user)




@app.route("/account")
def account():

    if "user_id" not in session:
        return redirect(url_for("home"))
    return render_template("pages/account.html")


@app.route("/maakpost")
def maakpost():
    return render_template("pages/maakpost.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/inloggen")
def inloggen():

    if session.get("user_id"):
        return redirect(url_for("home"))

    errors = session.pop("errors", {})
    old = session.pop("old", {})
    return render_template("pages/inloggen.html", errors=errors, old=old)


@app.route("/login/post", methods=["POST"])
def inloggenPost():
    email = request.form.get("email")
    password = request.form.get("password")

    errors = {}

    if not email:
        errors["email"] = "Email is verplicht"
    elif not re.match(EMAIL_REGEX, email):
        errors["email"] = "Ongeldige email"

    if not password:
        errors["password"] = "Wachtwoord is verplicht"

    if email and password:
        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            errors["invalid"] = "Wachtwoord of email is onjuist"

    if errors:
        session["errors"] = errors
        session["old"] = {
            "email": email
        }
        return redirect(url_for("inloggen"))

    session.permanent = True
    session["user_id"] = user.id
    session["username"] = user.username

    flash("Je bent ingelogd", "success")
    return redirect(url_for("inloggen"))


@app.route("/registreren")
def registreren():

    if session.get("user_id"):
        return redirect(url_for("home"))

    errors = session.pop("errors", {})
    old = session.pop("old", {})
    return render_template("pages/registreren.html", errors=errors, old=old)


@app.route("/registreren/create", methods=["POST"])
def createUser():
    data = request.form

    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    password_repeat = data.get("password_repeat", "")

    file = request.files.get('profile_image')
    filename = None

    errors = {}

    if not username:
        errors["username"] = "Gebruikersnaam is verplicht."
    elif len(username) < 3:
        errors["username"] = "Minimaal 3 karakters."

    if not email:
        errors["email"] = "Email is verplicht."
    elif not re.match(EMAIL_REGEX, email):
        errors["email"] = "Ongeldige email."

    if not password:
        errors["password"] = "Wachtwoord is verplicht."
    elif len(password) < 6:
        errors["password"] = "Minimaal 6 karakters."

    if not password_repeat:
        errors["password_repeat"] = "Herhaal wachtwoord."
    elif password != password_repeat:
        errors["password_repeat"] = "Komt niet overeen."

    if User.query.filter_by(email=email).first():
        errors["email"] = "Email al in gebruik."

    if User.query.filter_by(username=username).first():
        errors["username"] = "Gebruikersnaam al in gebruik."

    if errors:
        session["errors"] = errors
        session["old"] = {
            "username": username,
            "email": email,
        }
        return redirect(url_for("registreren"))

    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

    new_user = User(
        username=username,
        email=email,
        password_hash=password,
        profile_image=filename
    )

    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    session.permanent = True
    session["user_id"] = new_user.id
    session["username"] = username

    flash("Account aangemaakt en ingelogd!", "success")
    return redirect(url_for("registreren"))


@app.route("/maaknieuwsartikel")
def maaknieuwsartikel():
    if "user_id" not in session:
        flash("Je moet ingelogd zijn.", "error")
        return redirect(url_for("inloggen"))

    user = User.query.get(session["user_id"])

    if not user:
        session.clear()
        return redirect(url_for("inloggen"))

    if user.role not in ["admin", "editor"]:
        return redirect(url_for("home"))

    errors = session.pop("errors", {})
    old = session.pop("old", {})

    return render_template("/pages/maaknieuwsartikel.html", user=user, errors=errors, old=old)


@app.route("/article/create", methods=["POST"])
def createArticle():
    if "user_id" not in session:
        flash("Je moet ingelogd zijn om een nieuwsartikel aan te maken.", "error")
        return redirect(url_for("inloggen"))

    user = User.query.get(session["user_id"])

    if not user:
        session.clear()
        flash("Gebruiker niet gevonden. Log opnieuw in.", "error")
        return redirect(url_for("inloggen"))

    if user.role not in ["admin", "editor"]:
        flash("Je hebt geen toestemming om een nieuwsartikel aan te maken.", "error")
        return redirect(url_for("home"))

    data = request.form

    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    summary = data.get("summary", "").strip()
    content = data.get("content", "").strip()
    article_image = data.get("article_image", "").strip()
    is_published = data.get("is_published") == "on"

    errors = {}

    if not title:
        errors["title"] = "Titel is verplicht."
    elif len(title) < 3:
        errors["title"] = "Titel moet minimaal 3 karakters hebben."

    if not description:
        errors["description"] = "Beschrijving is verplicht."
    elif len(description) < 10:
        errors["description"] = "Beschrijving moet minimaal 10 karakters hebben."

    if not summary:
        errors["summary"] = "Samenvatting is verplicht."
    elif len(summary) < 10:
        errors["summary"] = "Samenvatting moet minimaal 10 karakters hebben."

    if not content:
        errors["content"] = "Content is verplicht."
    elif len(content) < 20:
        errors["content"] = "Content moet minimaal 20 karakters hebben."

    if NewsArticle.query.filter_by(slug=description).first():
        errors["description"] = "Deze beschrijving is al in gebruik."

    if errors:
        session["errors"] = errors
        old = {
            "title": title,
            "description": description,
            "summary": summary,
            "content": content,
            "article_image": article_image,
            "is_published": is_published
        }

        errors = session.pop("errors", {})
        old = session.pop("old", {})

        return render_template("/pages/maaknieuwsartikel.html", errors=errors, old=old)

        return redirect(url_for("maaknieuwsartikel"))

    new_article = NewsArticle(
        title=title,
        description=description,
        summary=summary,
        content=content,
        article_image=article_image if article_image else None,
        is_published=is_published,
        published_at=datetime.utcnow() if is_published else None,
        author_id=user.id
    )

    db.session.add(new_article)
    db.session.commit()

    flash("Nieuwsartikel succesvol aangemaakt.", "success")
    return redirect(url_for("home"))


@app.route("/users")
def get_users():
    users = User.query.all()

    return {
        "session": {
            "userid": session.get("user_id"),
            "username": session.get("username"),
        },
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "profile_image": user.profile_image,
                "email": user.email,
                "role": user.role,
                "created_at": str(user.created_at)
            }
            for user in users
        ]
    }


# admin routes


@app.route("/admin/users")
def users():
    return render_template("pages/admin/users.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
