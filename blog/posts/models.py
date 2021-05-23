from blog import db
from blog.users.models import User
from blog.comments.models import Comment


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


