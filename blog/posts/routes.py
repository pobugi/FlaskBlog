import datetime
from .models import Post, Like
from blog.comments.models import Comment
from blog.users.models import User
# from blog.posts.models import postlikes
from blog import app, db
from flask import redirect, render_template, request, flash, url_for, abort
from flask_login import login_required, current_user
from blog.users.routes import all_followers_of_user

def get_user_by_post_id(id):
    return db.session.query(User).select_from(User).join(Post).filter(User.id == Post.post_author_id).first()


@app.route('/users/<username>/wall', methods=['POST', 'GET'])
@login_required
def user(username):
    post_host = User.query.filter_by(username=username).first()
    # all_posts = Post.query.join(posts_users, (Post.id == posts_users.c.post_id)).filter_by(post_author_id=id).all()
    
    # all_users = User.query.all() replaced by the models function
    all_users = User.all_users()

    d = {}
    user_ids = []   # list of all user IDs
    for user in all_users:
        user_ids.append(user.id)
    # print('USER IDs:', user_ids)

    for user_id in user_ids:
        d[user_id] = all_followers_of_user(user_id) # a dictionary {user_id: [list of followers of user_id]}
    # print('d:', d)

    # users_already_liked_post = \
    #         db.session.query(User).select_from(User).join(Like).filter(Like.liked_post_id == k).all()

    if request.method == 'POST':
        new_post_post_author_id = post_host.id
        new_post_post_author_username = post_host.username
        new_post_post_title = request.form['post_title']
        new_post_post_content = request.form['post_content']
        new_post_date_added = datetime.datetime.utcnow()

        new_post = Post(post_author_id = new_post_post_author_id,
                        post_author_username = post_host.username,
                        post_title=new_post_post_title,
                        post_content = new_post_post_content,
                        post_date_added = new_post_date_added)

        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('user', username=username))

    # all_posts = Post.query.filter_by(post_author_id=post_host.id).order_by(Post.post_date_added.desc()).all()
    all_posts = Post.all_posts_by_author(post_host.id)
    
    all_followers = all_followers_of_user(post_host.id)
    print(all_followers)

    return render_template('user.html', post_host=post_host, 
                                        all_posts=all_posts,
                                        d=d,
                                        all_users=all_users,
                                        all_followers=all_followers)


@app.route('/feed')
@login_required
def feed():
    # all_posts = Post.query.order_by(Post.post_date_added.desc()).all()
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
        return redirect(request.referrer)
    return render_template('discuss_post.html', post_to_discuss=post_to_discuss,
                                                all_comments=all_comments)

@app.route('/posts/postid<int:id>/delete')
@login_required
def delete_post(id):
    post_to_delete = Post.get_post_by_id(id)
    if current_user.id == post_to_delete.post_author_id:
        db.session.delete(post_to_delete)
        db.session.commit()
    else:
        abort(405)
    return redirect(request.referrer)

@app.route('/posts/postid<int:id>/pushlike')
@login_required
def like_post(id):

    # post_to_be_liked = Post.query.get(id)
    post_to_be_liked = Post.get_post_by_id(id)

    users_already_liked_post = \
            db.session.query(User).select_from(User).join(Like).filter(Like.liked_post_id == id).all()

    if current_user not in users_already_liked_post:
        new_like = Like(like_author_id = current_user.id,
                        liked_post_id = id)
        post_to_be_liked.likes_increment()                
        # likes_increment = post_to_be_liked.post_likes_qty += 1
        db.session.add(new_like)
        flash('Like posted :)', 'success')

    else:
        like_to_delete = Like.query.filter(Like.like_author_id == current_user.id, Like.liked_post_id == id).first()
        # likes_decrement = post_to_be_liked.post_likes_qty -= 1
        post_to_be_liked.likes_decrement()                
        db.session.delete(like_to_delete)
        flash('Like deleted :(', 'danger')
    db.session.commit()

    print(post_to_be_liked)
    print('L=',len(users_already_liked_post))
    print(current_user in users_already_liked_post)
    # return redirect(url_for('discuss_post', id=post_to_be_liked.post_author_id))
    return redirect(request.referrer)
    # liked_post_host_id = post_to_be_liked.post_author_id

    # users_already_liked_post = User.query.join(postlikes, (User.id == postlikes.c.liked_user_id)).filter_by(liked_post_id=id).all()



    # users_already_liked_post = Like.query.filter_by(liked_post_id=id, like_author_id=current_user.id).all()

    # like_objects = Like.query.join(User, (id==Like.like_author_id)).filter_by(liked_post_id=id).all()

    # print(current_user in res)
    # print('PIZDAAAA', res)


    # if current_user in users_already_liked_post:
    #     return 'LIKE REMOVED!'

    # new_like = Like(like_author_id = current_user.id, 
    #                 liked_post_id = id)
    # db.session.add(new_like)
    # db.session.commit()

    # return redirect(url_for('user', id=3))
    # like = postlikes.insert().values(liked_post_id=id, liked_user_id=current_user.id)
    # db.session.execute(like)
    # db.session.commit()
    # return 'LIKE POSTED!'






    


