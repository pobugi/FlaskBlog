from blog import db, login_manager

# from flask_sqlalchemy import SQLAlchemy


# db = SQLAlchemy()

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

    @staticmethod
    def ensure_unique_username(name):
        """Ensure user name does not already exist"""
        if User.query.filter_by(name=name).first() is None:
            return name
        version = 1
        while True:
            old_name = name
            new_name = name + '_' + str(version)
            if User.query.filter_by(name=new_name).first() is None:
                break
            version += 1
        # flash('Your name has been changed to {} as user {} already exists.'.format(new_name, old_name), 'success')
        return new_name

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

class Post(db.Model):

    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    post_author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_author_username = db.Column(db.String(50), nullable=False)
    post_title = db.Column(db.String(50), nullable=False)
    post_content = db.Column(db.String(500), nullable=False)
    post_date_added = db.Column(db.DateTime, nullable=True)
    post_likes_qty = db.Column(db.Integer, default=0)

    comments = db.relationship('Comment', backref='post', cascade="all, delete", lazy='dynamic')

    def __str__(self):
        return 'Post ID: {}, Author: {}'.format(self.id, self.post_author_username)

    def likes_increment(self):
        self.post_likes_qty += 1

    def likes_decrement(self):
        self.post_likes_qty -= 1

    def get_post_by_id(id):
        return Post.query.get(id)

    @staticmethod
    def all_posts():
        return Post.query.order_by(Post.post_date_added.desc()).all()

    @staticmethod
    def all_posts_by_author(id):
        return Post.query.filter_by(post_author_id=id).order_by(Post.post_date_added.desc()).all()

    def who_liked_the_post(id):
        who_liked_the_post = db.session.query(User).select_from(User).join(Like).filter(Like.liked_post_id == id).all()
        return who_liked_the_post


class Like(db.Model):
    __tablename__ = 'like'
    id = db.Column(db.Integer, primary_key=True)
    like_author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    liked_post_id = db.Column(db.Integer, db.ForeignKey('post.id'))