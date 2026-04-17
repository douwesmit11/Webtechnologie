from app import app, db
from models import User

with app.app_context():
    db.session.query(User).delete()
    db.session.commit()

    users = [
        {"username": "Jur", "email": "admin@test.com", "role": "admin"},
        {"username": "Douwe", "email": "editor@test.com", "role": "editor"},
        {"username": "Bob", "email": "user@test.com", "role": "user"},
    ]

    for u in users:
        if not User.query.filter_by(email=u["email"]).first():
            user = User(**u)
            user.set_password("wachtwoord")
            db.session.add(user)

    db.session.commit()
    print("Gebruikers toegevoegd")
