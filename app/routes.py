from flask import redirect, render_template, flash, url_for, request
from datetime import date, datetime
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db
from app.forms import RegistrationForm, LoginForm, PostForm, CommentForm
from werkzeug.urls import url_parse
from app.models import User, Post, Comment


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=["GET", "POST"])
def index():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html',
                           title="Home",
                           posts=posts,
                           )


@app.route('/post/<int:post_number>', methods=['GET', 'POST'])
@login_required
def post(post_number):
    form = CommentForm()
    post = Post.query.filter_by(id=post_number).first_or_404()
    comments = post.all_comments().all()
    if form.validate_on_submit():
        # Strip beginning and ending <p> tags - until I find out how to do it in the editor
        if form.comment.data.startswith('<p>') and form.comment.data.endswith('</p>'):
            form.comment.data = form.comment.data[3:-4]
        comment = Comment(body=form.comment.data, commenter=current_user, blog_post=post)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('post', post_number=post_number))
    return render_template('post.html', post_number=post.id, title='title', form=form, post=post, comments=comments)



@app.route('/submit', methods=['GET', 'POST'])
@login_required
def submit():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, url=form.url.data, author=current_user)
        print(post.url)
        post.set_source(post.url)
        db.session.add(post)
        db.session.commit()
        flash(f'Your Post is now live')
        return redirect(url_for('index'))
    return render_template('submit.html',
                           title="Create Post",
                           form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(f'Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
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
    return render_template('register.html', title='Register', form=form)


@app.route('/block/<username>')
@login_required
def block(username):
    user = User.query.filter_by(username=username).first()
    if current_user.is_blocking(user):
        flash(f"Not sure how you managed that. You were already meant to be blocking {username}"
              f" already. So I guess don't trust me that it worked this time either")
        return redirect(request.referrer)
    if user is None:
        flash(f'Sorry but {username} does not exist. Which I guess is kind of the same as blocking them')
        return redirect(request.referrer)
    if user == current_user:
        flash(f"I guess I could let you block yourself, but I kind of don't see the point")
        return redirect(request.referrer)
    current_user.block(user)
    db.session.commit()
    flash(f"Good news, you won't see any comments from {username} anymore")
    return redirect(request.referrer)

@app.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    id = user.id
    last_seen = user.last_seen
    joined = user.joined
    about_you = user.about_you
    return render_template('profile.html',
                           user=user,)


@app.context_processor
def days():
    start_date = date(2018, 3, 28)
    today = date.today()
    days = (today - start_date).days
    return dict(days=days)
