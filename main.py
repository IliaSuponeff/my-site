import flask_login
from flask import Flask, redirect, render_template, url_for
from flask_dance.contrib.github import github
from flask_dance.contrib.google import google
from flask_login import logout_user, login_required, current_user
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError

from app.models import db, login_manager, set_like, is_liked, likes_count
from app.oauth import github_blueprint, google_blueprint

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./users.db"
app.secret_key = "supersecretkey"
app.register_blueprint(github_blueprint, url_prefix="/login")
app.register_blueprint(google_blueprint, url_prefix="/login")

db.init_app(app)
login_manager.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    liked = is_liked(current_user.get_id())
    return render_template(
        "index.html",
        is_liked=liked,
        count_likes=likes_count()
    )

@app.route('/resume')
def resume():
    return render_template('resume.html')

@app.route('/projects')
def projects():
    return render_template('projects.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route("/github")
def github_login():
    if not github.authorized:
        return redirect(url_for("github.login"))
    return redirect(url_for("index"))

@app.route("/google")
def google_login():
    try:
        if not google.authorized:
            return redirect(url_for("google.login"))
        res = google.get("/oauth2/v2/userinfo")
        return redirect(url_for("index"))
    except TokenExpiredError as e:
        return redirect(url_for("google.login"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/social_up")
@login_required
def social_up():
    if current_user.is_authenticated:
        set_like(current_user.get_id())

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)