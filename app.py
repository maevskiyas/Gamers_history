import os
import time
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_migrate import Migrate
from flask_login import login_user, logout_user, login_required, LoginManager, current_user
from werkzeug.utils import secure_filename
from forms import RegistrationForm, LoginForm, AddGameForm, ProfileForm, PasswordChangeForm, DeleteAccountForm
from models import db, User, Game, UserGame
from werkzeug.security import check_password_hash
from werkzeug.datastructures import FileStorage
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf


# Завантаження .env
load_dotenv()

# Ваш ключ API RAWG
API_KEY = 'fc0914e8d7e74e52a6d030cf75ee1309'
BASE_URL = 'https://api.rawg.io/api/games'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gamelibrary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# Завантаження обкладинок
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['AVATAR_UPLOAD_FOLDER'] = 'static/avatars'
os.makedirs(app.config['AVATAR_UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)
migrate = Migrate(app, db)

# Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = "login"

csrf = CSRFProtect(app)

# щоб мати csrf_token() у всіх шаблонах
@app.context_processor
def csrf_token_processor():
    return dict(csrf_token=generate_csrf)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route("/")
@login_required
def home():
    # Отримуємо ігри поточного користувача з таблиці UserGame
    user_games = UserGame.query.filter_by(user_id=current_user.id).all()
    
    # Передаємо ігри на шаблон
    return render_template("index.html", user_games=user_games)

@app.route("/games")
@login_required
def game_list():
    view = request.args.get('view', 'list')  # Отримуємо параметр 'view', або використовуємо 'list' за замовчуванням
    user_games = UserGame.query.filter_by(user_id=current_user.id).all()

    # Вибір шаблону на основі параметра 'view'
    if view == 'tiles':
        template = "games/tiles.html"
    else:
        template = "games/list.html"

    return render_template(template, user_games=user_games)

@app.route("/games/add", methods=["GET", "POST"])
@login_required
def add_game():
    form = AddGameForm()
    if form.validate_on_submit():
        cover_filename = None
        if form.cover.data and allowed_file(form.cover.data.filename):
            filename = secure_filename(form.cover.data.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
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

        flash("Гра додана до вашої бібліотеки!", "success")
        return redirect(url_for("game_list"))
    return render_template("games/add.html", form=form)


@app.route("/import")
@login_required
def import_games():
    return render_template("import.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash("Вхід успішний!", "success")
            return redirect(url_for("home"))
        else:
            flash("Невірне ім'я користувача або пароль", "danger")
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
            flash("Користувач з таким email вже існує", "warning")
            return redirect(url_for('register'))

        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('home') + "?_=" + str(int(time.time())))
    return render_template('auth/register.html', form=form)

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm(obj=current_user)

    # Відключення можливості змінювати ім'я користувача
    form.username.render_kw = {'disabled': True}  # Заборона на зміну імені користувача
    
    if form.validate_on_submit():
        if User.query.filter(User.email == form.email.data, User.id != current_user.id).first():
            flash("Цей email вже використовується", "warning")
            return redirect(url_for("profile"))

        # Оновлюємо тільки email, якщо він змінився
        current_user.email = form.email.data

        # Обробка аватара, тільки якщо було завантажено нове фото
        if form.avatar.data:
            avatar_file = form.avatar.data
            if isinstance(avatar_file, FileStorage):
                avatar_filename = secure_filename(avatar_file.filename)
                avatar_path = os.path.join(app.config['AVATAR_UPLOAD_FOLDER'], avatar_filename)
                avatar_file.save(avatar_path)
                current_user.avatar = avatar_filename

        # Збереження змін в базі даних
        db.session.commit()
        flash("Профіль оновлено", "success")
        return redirect(url_for("profile"))

    return render_template("users/profile.html", form=form)

@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    form = ProfileForm(obj=current_user)  # підставляємо поточні дані
    if form.validate_on_submit():
        # унікальність username/email (простий варіант)
        if User.query.filter(User.username==form.username.data, User.id!=current_user.id).first():
            flash("Це ім'я вже зайняте", "warning")
            return redirect(url_for("settings"))
        if User.query.filter(User.email==form.email.data, User.id!=current_user.id).first():
            flash("Цей email вже використовується", "warning")
            return redirect(url_for("settings"))

        current_user.username = form.username.data
        current_user.email = form.email.data

        # аплоад аватара (необов'язково)
        if form.avatar.data:
            f = form.avatar.data
            ext = f.filename.rsplit('.', 1)[-1].lower()
            filename = secure_filename(f"user{current_user.id}_{int(time.time())}.{ext}")
            path = os.path.join(app.config['AVATAR_UPLOAD_FOLDER'], filename)
            f.save(path)
            current_user.avatar = filename

        db.session.commit()
        flash("Профіль оновлено", "success")
        return redirect(url_for("settings"))
    return render_template("users/settings.html", form=form)

@app.route("/settings/password", methods=["GET", "POST"])
@login_required
def change_password():
    form = PasswordChangeForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash("Невірний поточний пароль", "danger")
            return redirect(url_for("change_password"))
        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash("Пароль змінено", "success")
        return redirect(url_for("settings"))
    return render_template("users/change_password.html", form=form)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # Логіка для відправлення електронного листа для скидання пароля
            # Тут має бути код для генерування і відправлення листа з посиланням для скидання пароля
            flash('Інструкції для скидання пароля надіслані на вашу електронну пошту', 'success')
            return redirect(url_for('login'))
        flash('Користувача з такою електронною адресою не знайдено', 'danger')
    return render_template('auth/reset_password.html', form=form)

@app.route("/settings/delete", methods=["GET", "POST"])
@login_required
def delete_account():
    form = DeleteAccountForm()
    if form.validate_on_submit():
        if form.confirm.data.strip().upper() != "DELETE":
            flash("Підтвердження не співпадає. Введіть DELETE.", "warning")
            return redirect(url_for("delete_account"))
        uid = current_user.id
        logout_user()
        # Видаляємо акаунт. Завдяки cascade="all, delete-orphan" зникнуть записи в UserGame
        user = db.session.get(User, uid)
        db.session.delete(user)
        db.session.commit()
        flash("Акаунт видалено", "success")
        return redirect(url_for("home"))
    return render_template("users/delete_account.html", form=form)

@app.route("/games/<int:game_id>/delete", methods=["POST"])
@login_required
def delete_user_game(game_id):
    user_game = UserGame.query.filter_by(user_id=current_user.id, game_id=game_id).first()
    if user_game:
        db.session.delete(user_game)
        db.session.commit()
        flash("Гру видалено з вашої бібліотеки", "success")
    else:
        flash("Цієї гри немає у вашій бібліотеці", "warning")
    
    # Після видалення перенаправляємо на головну сторінку
    return redirect(url_for("home"))

@app.route("/terms_of_service")
def terms_of_service():
    return render_template("terms_of_service.html")

@app.route("/privacy_policy")
def privacy_policy():
    return render_template("privacy_policy.html")

@app.route("/search", methods=["GET"])
def search_games():
    query = request.args.get('query', '')  # Отримуємо запит користувача
    if not query:
        flash("Будь ласка, введіть назву гри для пошуку", "warning")
        return redirect(url_for('home'))

    # Параметри запиту до API
    params = {
        'key': API_KEY,
        'search': query,
        'page_size': 10  # Обмежуємо кількість результатів
    }

    # Виконання запиту до API
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        games = data.get('results', [])
    else:
        games = []
        flash("Не вдалося знайти ігри, спробуйте ще раз", "danger")

    return render_template('index.html', user_games=[], games=games)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
