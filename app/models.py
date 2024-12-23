from gc import isenabled
from typing import Optional

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True)


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)

class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)


login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id) -> Optional[User]:
    return User.query.get(user_id)


def likes_count() -> int:
    return len(Like.query.all())


def is_liked(user_id) -> bool:
    user = load_user(user_id)
    if user is None:
        return False

    likes: list = Like.query.filter_by(user_id=user_id).all()
    return len(likes) > 0


def set_like(user_id):
    if is_liked(user_id):
        return

    new_like = Like(user_id=user_id)
    db.session.add(new_like)
    db.session.commit()
