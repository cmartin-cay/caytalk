from flask_wtf import FlaskForm
from sqlalchemy import func
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo

from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        # Check to see if the username exists, if it does make the new user choose a different username
        user = User.query.filter(func.lower(User.username) == func.lower(username.data)).first()
        if user:
            raise ValidationError(f'The username is already in use. Please select a different username')

    def validate_email(self, email):
        # Check to see if the email address exists, if it does make the new user choose a different address
        user = User.query.filter(func.lower(User.email) == func.lower(email.data)).first()
        if user:
            raise ValidationError(f'The email address is already in use. Please select a different address')