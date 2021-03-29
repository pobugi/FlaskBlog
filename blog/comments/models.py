from blog import db

from blog.users.models import User
from blog.posts.models import Post


class Comment(db.Model):

    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    comment_post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    comment_author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comment_author_username = db.Column(db.String(50), nullable=False)
    comment_content = db.Column(db.String(500), nullable=False)
    comment_date_added = db.Column(db.DateTime, nullable=True)
    post = db.relationship('Post',cascade="all,delete", backref=db.backref('post', lazy=True))

