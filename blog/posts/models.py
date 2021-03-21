from blog import db
from blog.users.models import User



# posts_users = db.Table('posts_users',
#                         db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
#                         db.Column('post_author_id', db.Integer, db.ForeignKey('user.id')))

# postlikes = db.Table('postlikes',
#                      db.Column('liked_post_id', db.Integer, db.ForeignKey('post.id')),
#                      db.Column('liked_user_id', db.Integer, db.ForeignKey('user.id')))


class Post(db.Model):

    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    post_author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_author_username = db.Column(db.String(50), nullable=False)
    post_title = db.Column(db.String(50), nullable=False)
    post_content = db.Column(db.String(500), nullable=False)
    post_date_added = db.Column(db.DateTime, nullable=True)
    post_likes_qty = db.Column(db.Integer, default=0)

    # likes = db.relationship('User', secondary=postlikes, backref=db.backref('postslikedbyuser', lazy=True))

    # post_likes_qty = db.Column(db.Integer, default=0)
    def __str__(self):
        return 'Post ID: {}, Author: {}'.format(self.id, self.post_author_username)

    def likes_increment(self):
        self.post_likes_qty += 1

    def likes_decrement(self):
        self.post_likes_qty -= 1

    
class Like(db.Model):
    __tablename__ = 'like'
    id = db.Column(db.Integer, primary_key=True)
    like_author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    liked_post_id = db.Column(db.Integer, db.ForeignKey('post.id'))


class Comment(db.Model):

    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    comment_post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    comment_author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comment_content = db.Column(db.String(500), nullable=False)
