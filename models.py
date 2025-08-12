from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Ініціалізація SQLAlchemy (один раз!)
db = SQLAlchemy()

# Проміжна таблиця для зв'язку гра ↔ жанр
game_genres = db.Table(
    "game_genres",
    db.Column("game_id", db.Integer, db.ForeignKey("game.id"), primary_key=True),
    db.Column("genre_id", db.Integer, db.ForeignKey("genre.id"), primary_key=True),
)

class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    avatar = db.Column(db.String(255))

    # Зв'язок з UserGame
    games = db.relationship("UserGame", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Game(db.Model):
    __tablename__ = "game"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    release_year = db.Column(db.Integer)
    platform = db.Column(db.String(50), nullable=False)
    rating = db.Column(db.Float)
    hours_played = db.Column(db.Float)
    cover = db.Column(db.String(255))  # filename або зовнішній URL
    extra_data = db.Column(db.JSON)      # додаткові поля від API (dict)
    steam_appid = db.Column(db.Integer, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    genres = db.relationship("Genre", secondary=game_genres, back_populates="games")
    user_links = db.relationship("UserGame", back_populates="game", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Game {self.title}>"


class Genre(db.Model):
    __tablename__ = "genre"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False, index=True)

    games = db.relationship("Game", secondary=game_genres, back_populates="genres")

    def __repr__(self):
        return f"<Genre {self.name}>"


class UserGame(db.Model):
    __tablename__ = "user_game"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey("game.id"), nullable=False)
    hours_played = db.Column(db.Integer, default=0)
    rating = db.Column(db.Integer)  # 1–10 або null
    imported_from = db.Column(db.String(64))  # 'steam', 'manual', 'csv'
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", back_populates="games")
    game = db.relationship("Game", back_populates="user_links")

    def __repr__(self):
        return f"<UserGame {self.user_id} ↔ {self.game_id}>"