from flask import url_for, flash, redirect, request, render_template
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse
from werkzeug.utils import redirect
from app import db
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User
from app.auth import bp


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(f'Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Login', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    # User already logged in, can't login twice, return to index
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    # valid form submitted, register User
    if form.validate_on_submit():
        # noinspection PyArgumentList
        user = User(first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    username=form.username.data,
                    email=form.email.data,
                    )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Congratulations, you are now a registered user!'
              f' Please consider going to your profile to tell us a little more about you')
        return redirect(url_for('index'))
    # No form data submitted or incorrect data, render the registration template
    return render_template('auth/register.html', title='Register', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))