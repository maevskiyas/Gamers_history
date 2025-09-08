from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, BooleanField,
    SelectField, IntegerField, FloatField
)
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional, NumberRange
from flask_wtf.file import FileField, FileAllowed
from flask_babel import lazy_gettext as _l


class LoginForm(FlaskForm):
    username = StringField(_l("Username"), validators=[DataRequired()])
    password = PasswordField(_l("Password"), validators=[DataRequired()])
    remember = BooleanField(_l("Remember me"))
    submit = SubmitField(_l("Log in"))


class RegistrationForm(FlaskForm):
    username = StringField(_l("Username"), validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField(_l("Email"), validators=[DataRequired(), Email()])
    password = PasswordField(_l("Password"), validators=[DataRequired()])
    confirm_password = PasswordField(_l("Confirm Password"), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l("Sign up"))


class AddGameForm(FlaskForm):
    title = StringField(_l("Game title"), validators=[DataRequired()])
    release_year = IntegerField(_l("Release year"), validators=[Optional(), NumberRange(min=1970, max=2100)])
    platform = SelectField(
        _l("Platform"),
        choices=[("PC", _l("PC")), ("PS5", _l("PlayStation 5")), ("Xbox", _l("Xbox"))],
        validators=[DataRequired()]
    )
    hours_played = FloatField(_l("Hours played"), validators=[Optional(), NumberRange(min=0)])
    rating = IntegerField(_l("Rating"), validators=[Optional(), NumberRange(min=1, max=10)])
    cover = FileField(_l("Cover"), validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], _l('Images only!'))])
    submit = SubmitField(_l("Save"))


class ProfileForm(FlaskForm):
    username = StringField(_l("Username"), validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField(_l("Email"), validators=[DataRequired(), Email()])
    avatar = FileField(_l("Profile photo"), validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], _l('Images only!'))])
    submit = SubmitField(_l("Save"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # забороняємо зміну імені користувача (як і було)
        self.username.render_kw = {'disabled': True}


class PasswordChangeForm(FlaskForm):
    current_password = PasswordField(_l("Current password"), validators=[DataRequired()])
    new_password = PasswordField(_l("New password"), validators=[DataRequired(), Length(min=6)])
    confirm_new_password = PasswordField(_l("Confirm new password"), validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField(_l("Change password"))


class DeleteAccountForm(FlaskForm):
    confirm = StringField(_l("Type DELETE to confirm"), validators=[DataRequired()])
    submit = SubmitField(_l("Delete account"))


class ResetPasswordForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Reset password'))
