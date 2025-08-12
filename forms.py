from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField, FloatField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional, NumberRange
from flask_wtf.file import FileField, FileAllowed

class LoginForm(FlaskForm):
    username = StringField("Ім'я користувача", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember = BooleanField("Запам’ятати мене")
    submit = SubmitField("Увійти")

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class AddGameForm(FlaskForm):
    title = StringField("Назва гри", validators=[DataRequired()])
    release_year = IntegerField("Рік випуску", validators=[Optional(), NumberRange(min=1970, max=2100)])
    platform = SelectField("Платформа", choices=[("PC", "PC"), ("PS5", "PlayStation 5"), ("Xbox", "Xbox")], validators=[DataRequired()])
    hours_played = FloatField("Годин зіграно", validators=[Optional(), NumberRange(min=0)])
    rating = IntegerField("Оцінка", validators=[Optional(), NumberRange(min=1, max=10)])
    cover = FileField("Обкладинка", validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Лише зображення!')])
    submit = SubmitField("Зберегти")

class ProfileForm(FlaskForm):
    username = StringField("Ім'я користувача", validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    avatar = FileField("Фото профілю", validators=[FileAllowed(['jpg','jpeg','png','gif'], 'Лише зображення!')])
    submit = SubmitField("Зберегти")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Вимикаємо поле для редагування імені користувача
        self.username.render_kw = {'disabled': True}

class PasswordChangeForm(FlaskForm):
    current_password = PasswordField("Поточний пароль", validators=[DataRequired()])
    new_password = PasswordField("Новий пароль", validators=[DataRequired(), Length(min=6)])
    confirm_new_password = PasswordField("Підтвердіть новий пароль",
                                         validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField("Змінити пароль")

class DeleteAccountForm(FlaskForm):
    confirm = StringField("Введіть DELETE для підтвердження", validators=[DataRequired()])
    submit = SubmitField("Видалити акаунт")

class ResetPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Відновити пароль')