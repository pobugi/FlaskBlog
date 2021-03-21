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


    posts = db.relationship('Post', backref='user', lazy='dynamic')
    likes = db.relationship('Like', backref='user', lazy='dynamic')
    comments = db.relationship('Comment', backref='user', lazy='dynamic')
    # followers = db.relationship('Follower', backref='user', lazy='dynamic')
    # followers = db.relationship('User', secondary=followers, backref=db.backref('followers_of_user', lazy=True))


    def __str__(self):
        return 'User {}'.format(self.username)


# class Follower(db.Model):
#     __tablename__ = 'follower'
#     id = db.Column(db.Integer, primary_key=True)
#     followed_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     follower_id = db.Column(db.Integer, db.ForeignKey('user.id'))



@login_manager.user_loader
def load_user(user_id):
    """User loader function"""
    return User.query.get(user_id)