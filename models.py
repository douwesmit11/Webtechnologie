from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, MappedColumn
from datetime import datetime
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    __table_args__ = (
        db.CheckConstraint(
            "role IN ('user', 'editor', 'admin')",
            name="ck_users_role"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    profile_image = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(20), nullable=False, default="user")
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    posts = db.relationship(
        "UserPost",
        back_populates="author",
        cascade="all, delete-orphan",
        lazy=True
    )

    comments = db.relationship(
        "PostComment",
        back_populates="author",
        cascade="all, delete-orphan",
        lazy=True
    )

    news_articles = db.relationship(
        "NewsArticle",
        back_populates="author",
        lazy=True
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def can_publish_news(self):
        return self.role in ("editor", "admin")

    def __repr__(self):
        return f"<User {self.username}>"



class UserPost(db.Model):
    __tablename__ = "user_posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), unique=True, nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    is_published = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    author_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    author = db.relationship("User", back_populates="posts")

    comments = db.relationship(
        "PostComment",
        back_populates="post",
        cascade="all, delete-orphan",
        lazy=True
    )

    def __repr__(self):
        return f"<UserPost {self.title}>"



class PostComment(db.Model):
    __tablename__ = "post_comments"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    post_id = db.Column(
        db.Integer,
        db.ForeignKey("user_posts.id"),
        nullable=False,
        index=True
    )

    author_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    post = db.relationship("UserPost", back_populates="comments")
    author = db.relationship("User", back_populates="comments")

    def __repr__(self):
        return f"<PostComment {self.id}>"



class NewsCategory(db.Model):
    __tablename__ = "news_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False, index=True)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    articles = db.relationship(
        "NewsArticle",
        back_populates="category",
        lazy=True
    )

    def __repr__(self):
        return f"<NewsCategory {self.name}>"



class NewsArticle(db.Model):
    __tablename__ = "news_articles"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(220), nullable=False)
    slug = db.Column(db.String(240), unique=True, nullable=False, index=True)
    summary = db.Column(db.String(500), nullable=True)
    content = db.Column(db.Text, nullable=False)
    cover_image = db.Column(db.String(255), nullable=True)
    featured = db.Column(db.Boolean, nullable=False, default=False)
    is_published = db.Column(db.Boolean, nullable=False, default=False)
    published_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    author_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("news_categories.id"),
        nullable=True,
        index=True
    )

    author = db.relationship("User", back_populates="news_articles")
    category = db.relationship("NewsCategory", back_populates="articles")

    def __repr__(self):
        return f"<NewsArticle {self.title}>"



def init_database(app):
    db.init_app(app)

    with app.app_context():
        db.create_all()