from flask import (Flask, g, render_template, flash, redirect, url_for)
from flask_bcrypt import check_password_hash
from flask_login import (LoginManager, login_user, logout_user,
                         login_required, current_user)

import forms
import models

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = 'asdfioeriugn12,wdfiommiojf!euihreg'

# login manager setting
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# load user
@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user


@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response


@app.route('/login', methods=('GET','POST'))
def login():
    form = forms.LoginForm()
    try:
        user = models.User.get(models.User.email == form.email.data)
    except models.DoesNotExist:
        flash("Your email or password doens't match!", "error")
    else:
        if check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("You've been logged in!", "success")
            return redirect(url_for('index'))
        else:
            flash("Your email or password doens't match!", "error")
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required  # decoration for only logged in user contents
def logout():
    logout_user()  # delete cookie
    flash("You've been logged out! Come back soon,", "success")
    return redirect(url_for('index'))


@app.route('/register', methods=('GET','POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash("Yay, you registerd!", "success")
        models.User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
        )
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/new_post', methods=('GET', 'POST'))
@login_required
def post():
    form = forms.PostForm()
    if form.validate_on_submit():
        models.Post.create(user=g.user._get_current_object(),
                           content=form.content.data.strip())
        flash("Message posted! Thanks!", "success")
        return redirect(url_for('index'))
    return render_template('post.html', form=form)


@app.route('/')
def index():
    stream = models.Post.select().limit(100)
    return render_template('stream.html', stream=stream)


@app.route('/stream')
@app.route('/stream/<username>')
def stream(username=None):
    template = 'stream.html'
    if username and username != current_user.username:
        user = models.User.select().where(models.User.username**username).get()
        stream = user.posts.limit(100)
    else:
        stream = current_user.get_stream().limit(100)
        user = current_user
    if username:
        template = 'user_stream.html'
    return render_template(template, stream=stream, user=user)


if __name__ == '__main__':

    # initialize database
    models.initialize()
    # create admin user
    try:
        models.User.create_user(
            username='archie J',
            email='archieJ@hotmail.com',
            password='password',
            admin=True
        )
    except ValueError:
        pass
    app.run(debug=DEBUG, host=HOST, port=PORT)
