import os
import time
import requests
from requests import RequestException
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_migrate import Migrate
from flask_login import (
    login_user, logout_user, login_required, LoginManager, current_user
)
from flask_babel import Babel, _
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import RequestEntityTooLarge
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf

from forms import (
    RegistrationForm, LoginForm, AddGameForm,
    ProfileForm, PasswordChangeForm, DeleteAccountForm
    # ResetPasswordForm  # ← увімкни, якщо реально є у forms.py
)
from models import db, User, Game, UserGame

# -------------------- Конфіг/ініціалізація --------------------

load_dotenv()

API_KEY = os.getenv("RAWG_API_KEY")
BASE_URL = 'https://api.rawg.io/api/games'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gamelibrary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# i18n
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_SUPPORTED_LOCALES'] = ['en', 'uk']

# Файли/обмеження
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['AVATAR_UPLOAD_FOLDER'] = 'static/avatars'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['AVATAR_UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)
migrate = Migrate(app, db)

# Логін
login_manager = LoginManager(app)
login_manager.login_view = "login"

# CSRF
csrf = CSRFProtect(app)

# Щоб у всіх шаблонах працювало {{ csrf_token() }}
@app.context_processor
def csrf_token_processor():
    return dict(csrf_token=generate_csrf)

# i18n: вибір мови через ?lang=uk|en (і збереження у сесії)
def get_locale():
    lang = request.args.get('lang')
    if lang in app.config['BABEL_SUPPORTED_LOCALES']:
        session['lang'] = lang
        return lang
    return session.get('lang', app.config['BABEL_DEFAULT_LOCALE'])

babel = Babel(app, locale_selector=get_locale)

# (підстраховка) зробимо _ доступним у Jinja-глобалах
app.jinja_env.globals.update(_=_)

# -------------------- Допоміжні --------------------

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def fetch_popular_games(limit=10):
    try:
        params = {'key': API_KEY, 'ordering': '-rating', 'page_size': limit}
        r = requests.get(BASE_URL, params=params, timeout=10)
        if r.status_code == 200:
            return r.json().get('results', [])
    except RequestException:
        pass
    return []
# -------------------- Роути --------------------

@app.route("/")
@login_required
def home():
    user_games = UserGame.query.filter_by(user_id=current_user.id).all()
    popular_games = []
    # якщо бібліотека порожня — тягнемо популярні ігри
    if not user_games:
        popular_games = fetch_popular_games(limit=10)
    return render_template("index.html", user_games=user_games, popular_games=popular_games)

@app.route("/games")
@login_required
def game_list():
    view = request.args.get('view', 'list')
    query = request.args.get('query', '').strip()
    user_games = UserGame.query.filter_by(user_id=current_user.id).all()

    games = []
    try:
        if query:
            # Пошук
            params = {'key': API_KEY, 'search': query, 'page_size': 10}
        else:
            # Популярні зараз (без пошуку)
            # варіанти ordering: -added (часто додавані), -rating (високо оцінені), -metacritic
            params = {'key': API_KEY, 'ordering': '-added', 'page_size': 10}

        resp = requests.get(BASE_URL, params=params, timeout=10)
        if resp.ok:
            games = resp.json().get('results', []) or []
        else:
            flash(_("Couldn't fetch games, please try again."), "warning")
    except requests.RequestException:
        flash(_("Network error while searching games."), "danger")

    template = "games/tiles.html" if view == "tiles" else "games/list.html"
    return render_template(template, user_games=user_games, games=games, query=query)

# Додавання гри з RAWG-пошуку (або вручну, якщо дані прийшли у формі)
@app.route("/games/add/<int:game_id>", methods=["POST"])
@login_required
def add_game_to_library(game_id):
    game = Game.query.get(game_id)

    if not game:
        title = request.form.get('title') or _("Unknown game")
        platform = request.form.get('platform') or _("Unknown")
        release_year = request.form.get('release_year')
        cover_url = request.form.get('cover_url')

        cover_filename = None
        if cover_url:
            try:
                r = requests.get(cover_url, timeout=10)
                if r.status_code == 200:
                    ext = cover_url.rsplit('.', 1)[-1].split('?')[0]
                    cover_filename = f"{game_id}_{int(time.time())}.{ext}"
                    with open(os.path.join(app.config['UPLOAD_FOLDER'], cover_filename), 'wb') as f:
                        f.write(r.content)
            except requests.RequestException:
                cover_filename = None

        game = Game(
            id=game_id,
            title=title,
            platform=platform,
            release_year=release_year,
            cover=cover_filename
        )
        db.session.add(game)
        db.session.commit()

    existing_link = UserGame.query.filter_by(user_id=current_user.id, game_id=game.id).first()
    if existing_link:
        flash(_("This game is already in your library."), "warning")
    else:
        user_game = UserGame(
            user_id=current_user.id,
            game_id=game.id,
            hours_played=0,
            rating=0,
            imported_from="rawg"
        )
        db.session.add(user_game)
        db.session.commit()
        flash(_("Game added to your library!"), "success")

    return redirect(url_for('game_list'))

# Редагування гри (власного запису)
@app.route("/games/<int:game_id>/edit", methods=["GET", "POST"])
@login_required
def edit_game(game_id):
    user_game = UserGame.query.filter_by(user_id=current_user.id, game_id=game_id).first()
    if not user_game:
        flash(_("This game is not in your library."), "warning")
        return redirect(url_for("game_list"))

    form = AddGameForm(obj=user_game.game)

    if form.validate_on_submit():
        user_game.game.title = form.title.data
        user_game.game.platform = form.platform.data
        user_game.game.release_year = form.release_year.data
        user_game.hours_played = form.hours_played.data or 0
        user_game.rating = form.rating.data

        if form.cover.data and isinstance(form.cover.data, FileStorage):
            if allowed_file(form.cover.data.filename):
                filename = secure_filename(form.cover.data.filename)
                form.cover.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                user_game.game.cover = filename

        db.session.commit()
        flash(_("Game data updated"), "success")
        return redirect(url_for("game_list"))

    return render_template("games/edit.html", form=form, user_game=user_game)

# Ручне додавання гри
@app.route("/games/add", methods=["GET", "POST"])
@login_required
def add_game():
    form = AddGameForm()

    # 👇 важливо: choices для SelectField (підлаштуй під свій список)
    form.platform.choices = [
        ("PC", "PC"),
        ("PlayStation", "PlayStation"),
        ("Xbox", "Xbox"),
        ("Nintendo", "Nintendo"),
        ("Mobile", "Mobile"),
        ("Other", "Other"),
    ]

    if form.validate_on_submit():
        cover_filename = None
        if form.cover.data and allowed_file(form.cover.data.filename):
            filename = secure_filename(form.cover.data.filename)
            form.cover.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cover_filename = filename

        game = Game(
            title=form.title.data,
            release_year=form.release_year.data,
            platform=form.platform.data,
            cover=cover_filename,
        )
        db.session.add(game)
        db.session.commit()

        user_game = UserGame(
            user_id=current_user.id,
            game_id=game.id,
            hours_played=form.hours_played.data or 0,
            rating=form.rating.data,
            imported_from="manual",
        )
        db.session.add(user_game)
        db.session.commit()

        flash(_("Game added to your library!"), "success")
        # збережемо активний вигляд (list/tiles), якщо є
        view = request.args.get("view", "list")
        return redirect(url_for("game_list", view=view))

    # 🟢 якщо GET або форма невалідна — показуємо форму з помилками
    return render_template("games/add.html", form=form)

@app.route("/games/<int:game_id>/delete", methods=["POST"])
@login_required
def delete_user_game(game_id):
    user_game = UserGame.query.filter_by(user_id=current_user.id, game_id=game_id).first()
    if user_game:
        db.session.delete(user_game)
        db.session.commit()
        flash(_("Game removed from your library"), "success")
    else:
        flash(_("This game is not in your library."), "warning")
    # Повертаємось туди, звідки прийшли (або на список)
    return redirect(request.referrer or url_for("game_list"))

@app.route("/import")
@login_required
def import_games():
    return render_template("import.html")

# Вхід/вихід/реєстрація
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash(_("Signed in successfully!"), "success")
            return redirect(url_for("home"))
        else:
            flash(_("Invalid username or password"), "danger")
    return render_template("auth/login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash(_("A user with this email already exists"), "warning")
            return redirect(url_for('register'))

        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('home') + "?_=" + str(int(time.time())))
    return render_template('auth/register.html', form=form)

# Профіль/налаштування
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    # Забороняємо зміну username у цій формі (дизайн-рішення)
    form.username.render_kw = {'disabled': True}
    
    if form.validate_on_submit():
        if User.query.filter(User.email == form.email.data, User.id != current_user.id).first():
            flash(_("This email is already in use"), "warning")
            return redirect(url_for("profile"))

        current_user.email = form.email.data

        if form.avatar.data and isinstance(form.avatar.data, FileStorage):
            avatar_filename = secure_filename(form.avatar.data.filename)
            avatar_path = os.path.join(app.config['AVATAR_UPLOAD_FOLDER'], avatar_filename)
            form.avatar.data.save(avatar_path)
            current_user.avatar = avatar_filename

        db.session.commit()
        flash(_("Profile updated"), "success")
        return redirect(url_for("profile"))

    return render_template("users/profile.html", form=form)

@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        if User.query.filter(User.username == form.username.data, User.id != current_user.id).first():
            flash(_("This username is taken"), "warning")
            return redirect(url_for("settings"))
        if User.query.filter(User.email == form.email.data, User.id != current_user.id).first():
            flash(_("This email is already in use"), "warning")
            return redirect(url_for("settings"))

        current_user.username = form.username.data
        current_user.email = form.email.data

        if form.avatar.data and isinstance(form.avatar.data, FileStorage):
            ext = form.avatar.data.filename.rsplit('.', 1)[-1].lower()
            filename = secure_filename(f"user{current_user.id}_{int(time.time())}.{ext}")
            path = os.path.join(app.config['AVATAR_UPLOAD_FOLDER'], filename)
            form.avatar.data.save(path)
            current_user.avatar = filename

        db.session.commit()
        flash(_("Profile updated"), "success")
        return redirect(url_for("settings"))
    return render_template("users/settings.html", form=form)

@app.route("/settings/password", methods=["GET", "POST"])
@login_required
def change_password():
    form = PasswordChangeForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash(_("Wrong current password"), "danger")
            return redirect(url_for("change_password"))
        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash(_("Password changed"), "success")
        return redirect(url_for("settings"))
    return render_template("users/change_password.html", form=form)

@app.route("/settings/delete", methods=["GET", "POST"])
@login_required
def delete_account():
    form = DeleteAccountForm()
    if form.validate_on_submit():
        if form.confirm.data.strip().upper() != "DELETE":
            flash(_("Confirmation does not match. Type DELETE."), "warning")
            return redirect(url_for("delete_account"))
        uid = current_user.id
        logout_user()
        user = db.session.get(User, uid)
        db.session.delete(user)
        db.session.commit()
        flash(_("Account deleted"), "success")
        return redirect(url_for("home"))
    return render_template("users/delete_account.html", form=form)

@app.route("/terms_of_service")
def terms_of_service():
    return render_template("terms_of_service.html")

@app.route("/privacy_policy")
def privacy_policy():
    return render_template("privacy_policy.html")

# Пошук ігор (на головній через форму)
@app.route("/search", methods=["GET"])
@login_required
def search_games():
    query = request.args.get('query', '')
    if not query:
        flash(_("Please enter a game title"), "warning")
        return redirect(url_for('home'))

    games = []
    params = {'key': API_KEY, 'search': query, 'page_size': 20}
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        if response.status_code == 200:
            games = response.json().get('results', [])
        else:
            flash(_("Couldn't fetch games, please try again."), "danger")
    except requests.RequestException:
        flash(_("Network error while searching games."), "danger")

    user_games = UserGame.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', user_games=user_games, games=games)

# Обробка завеликого файлу
@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    flash(_("File is too large. Max size is 2MB."), "warning")
    return redirect(request.url)

# -------------------- entrypoint --------------------
if __name__ == "__main__":
    app.run(debug=True, port=5001)
