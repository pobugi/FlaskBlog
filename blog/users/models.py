from blog import db, login_manager
from flask_login import UserMixin


followers = db.Table('followers',
                    db.Column('id', db.Integer, primary_key=True),
                     db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')))


class User(UserMixin, db.Model):

    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(500), nullable=False)
    firstname = db.Column(db.String(50), default='Firstname')
    lastname = db.Column(db.String(50), default='Lastname')
    city = db.Column(db.String(50), default='Moscow')
    birthdate = db.Column(db.String(50), nullable=True, default='1990-01-01')
    gender = db.Column(db.String(50), default='Male')
    is_confirmed = db.Column(db.Boolean, nullable=False, default=False)


    registration_date = db.Column(db.DateTime, nullable=True)
    userpic = db.Column(db.String(30), default='default.jpg')

    followers_qty = db.Column(db.Integer, default=0)


    posts = db.relationship('Post', backref='user', cascade="all, delete", lazy='dynamic')
    likes = db.relationship('Like', backref='user', cascade="all, delete", lazy='dynamic')

    def __str__(self):
        return 'User {}'.format(self.username)

    def all_users():
        return User.query.all()
    
    def get_user_by_username(username):
        return User.query.filter_by(username=username).first()

    def all_followers(id):
        return User.query.join(followers, (User.id == followers.c.follower_id)).filter_by(user_id=id).all()

    def all_followed_by_user(id):
        return User.query.join(followers, (User.id == followers.c.user_id)).filter_by(follower_id=id).all()


@login_manager.user_loader
def load_user(user_id):
    """User loader function"""
    return User.query.get(user_id)