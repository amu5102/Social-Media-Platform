# app.py
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models import db, User, Post, Like, Comment
from forms import RegistrationForm, PostForm, CommentForm
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, password=form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful!')
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route('/')
@login_required
def index():
    posts = Post.query.all()
    form = PostForm()
    return render_template('index.html', posts=posts, form=form)

@app.route('/create_post', methods=['POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        image_url = None
        if form.image.data:
            image_url = save_image(form.image.data)
        new_post = Post(content=form.content.data, image_url=image_url, user_id=current_user.id)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('index'))
    return redirect(url_for('index'))

def save_image(image):
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
    image.save(image_path)
    return image_path

@app.route('/like/<int:post_id>')
@login_required
def like(post_id):
    like = Like.query.filter_by(post_id=post_id, user_id=current_user.id).first()
    if not like:
        new_like = Like(post_id=post_id, user_id=current_user.id)
        db.session.add(new_like)
    else:
        db.session.delete(like)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/comment/<int:post_id>', methods=['POST'])
@login_required
def comment(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        new_comment = Comment(content=form.content.data, post_id=post_id, user_id=current_user.id)
        db.session.add(new_comment)
        db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
