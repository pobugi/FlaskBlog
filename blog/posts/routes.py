import datetime
from .models import Post, Like
from blog.comments.models import Comment
from blog.users.models import User
from blog import app, db
from flask import redirect, render_template, request, flash, url_for, abort
from flask_login import login_required, current_user
from blog.users.routes import all_followers_of_user


all_users = User.all_users()  # list of all FlaskBlog users

user_ids = [user.id for user in all_users]  # list of user ids all FlaskBlog users
flwrs_dict = {usr: all_followers_of_user(usr) for usr in user_ids}  # dict {user_id: [followers of user_id]}


def get_user_by_post_id(id):
    # returns the "host" of a post
    return db.session.query(User).select_from(User).join(Post).filter(User.id == Post.post_author_id).first()


@app.route('/users/<username>/wall', methods=['POST', 'GET'])
@login_required
def user(username):
    # user wall view function
    post_host = User.query.filter_by(username=username).first()  # wall host
    all_users = User.all_users()  # list of all FlaskBlog users

    d = {}
    user_ids = []   # list of all user IDs
    for user in all_users:
        user_ids.append(user.id)

    for user_id in user_ids:
        d[user_id] = all_followers_of_user(user_id) # a dictionary {user_id: [list of followers of user_id]}

    if request.method == 'POST':
        new_post_post_author_id = post_host.id
        new_post_post_title = request.form['post_title']
        new_post_post_content = request.form['post_content']
        new_post_date_added = datetime.datetime.utcnow()

        new_post = Post(post_author_id=new_post_post_author_id,
                        post_author_username=post_host.username,
                        post_title=new_post_post_title,
                        post_content=new_post_post_content,
                        post_date_added=new_post_date_added)

        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('user', username=username))  # redirect to the user wall page

    all_posts = Post.all_posts_by_author(post_host.id)  # all posts of the wall host user
    all_followers = all_followers_of_user(post_host.id)  # all followers of the wall host user

    return render_template('user.html', post_host=post_host, 
                                        all_posts=all_posts,
                                        d=d,
                                        all_users=all_users,
                                        all_followers=all_followers)


@app.route('/feed')
@login_required
def feed():
    all_posts = Post.all_posts()
    return render_template('feed.html', all_posts=all_posts, get_user_by_post_id=get_user_by_post_id)


@app.route('/posts/postid<int:id>/discuss', methods=['POST', 'GET'])
@login_required
def discuss_post(id):
    post_to_discuss = Post.query.get(id)
    all_comments = Comment.query.filter_by(comment_post_id=id).order_by(Comment.comment_date_added.desc()).all()
    if request.method == 'POST':

        comment_post_id = post_to_discuss.id
        comment_author_id = current_user.id
        comment_author_username = current_user.username
        comment_content = request.form['post_comment']
        comment_date_added = datetime.datetime.utcnow()


        new_post_comment = Comment(comment_post_id=comment_post_id,
                                    comment_author_id=comment_author_id,
                                    comment_author_username=comment_author_username,
                                    comment_content=comment_content,
                                    comment_date_added = comment_date_added)
        db.session.add(new_post_comment)
        db.session.commit()
        flash('Commend added', 'success')
        app.logger.info('Comment added')
        return redirect(request.referrer)
    return render_template('discuss_post.html', post_to_discuss=post_to_discuss,
                                                all_comments=all_comments,
                                                flwrs_dict=flwrs_dict)


@app.route('/posts/postid<int:id>/delete')
@login_required
def delete_post(id):
    post_to_delete = Post.get_post_by_id(id)
    if current_user.id == post_to_delete.post_author_id:
        db.session.delete(post_to_delete)
        db.session.commit()
    else:
        abort(405)
    return redirect(url_for('user', username=current_user.username))


@app.route('/posts/postid<int:id>/pushlike')
@login_required
def like_post(id):
    #  put / remove like on a post
    post_to_be_liked = Post.get_post_by_id(id)  # Post object which is intended to be liked

    # list of users who already liked the post:
    # users_already_liked_post = \
    #         db.session.query(User).select_from(User).join(Like).filter(Like.liked_post_id == id).all()
    users_already_liked_post = Post.who_liked_the_post(id)

    #  if current not yet liked the post, create new like instance
    if current_user not in users_already_liked_post:
        new_like = Like(like_author_id=current_user.id,
                        liked_post_id=id)
        post_to_be_liked.likes_increment()  # call of likes increment method
        db.session.add(new_like)
        flash('Like posted :)', 'success')
        app.logger.info('Like posted')

    # if current user already liked the post, remove that like:
    else:
        # query the like to delete: select by bost id & user id
        like_to_delete = Like.query.filter(Like.like_author_id == current_user.id, Like.liked_post_id == id).first()
        post_to_be_liked.likes_decrement() # call of likes decrement method
        db.session.delete(like_to_delete)
        flash('Like deleted :(', 'danger')
        app.logger.info('Like removed')
    db.session.commit()

    return redirect(request.referrer)  # redirect to the initial page
