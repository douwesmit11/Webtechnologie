from flask_sqlalchemy import SQLALCHEMY
from sqlalchemy import Mapped, MappedColumn

db = SQLAlchemy()

class User(db.Model):
    id: Mapped[int] = MappedColumn(primary_key=True)
    email: Mapped[str]
    password : Mapped[str]


    def __init__(self, email:str, password: str):
        self.email = email
        self.password = password