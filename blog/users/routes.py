import datetime
import secrets
import os
from .models import User, followers
from blog.posts.models import Post
from blog import email_sender
from blog import app, db, photos, basedir, mail
from blog.token import generate_confirmation_token, confirm_token
from flask import redirect, render_template, request, flash, url_for, abort
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from blog.config import Config
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

s = URLSafeTimedSerializer(Config.SECRET_KEY)


@app.route('/users/delete/<id>')
@login_required
def delete_user(id):
    """
    Delete user function
    """
    user_to_delete = User.query.get(id)
    db.session.delete(user_to_delete)
    db.session.commit()
    flash('User deleted', 'danger')
    app.logger.warning('User deleted.')
    return redirect(request.referrer)


@app.route('/')
def index():
    """
    Index page view
    """
    return redirect(url_for('feed'))


@app.route('/send_confirmation_email/<email_address>')
@login_required
def send_confirmation_email(email_address):
    """
    Sending confirmation email functions
    """
    token = generate_confirmation_token(email_address)
    email_sender.send_confirmation_email(email=email_address, token=token)
    flash('Please check your email and follow the link', 'success')
    app.logger.info('Confirmation e-mail has been sent.')
    return redirect(request.referrer)


@app.route('/confirm_email/<token>')
@login_required
def confirm_email(token):
    """
    E-mail confirmation function
    """
    try:
        email = confirm_token(token)
    except SignatureExpired:
        return 'Token has expired'
    user_to_confirm = User.query.filter_by(email=email).first_or_404()
    if user_to_confirm.is_confirmed:
        return 'This user already confirmed'
    else:
        user_to_confirm.is_confirmed = True
        db.session.add(user_to_confirm)
        db.session.commit()
        flash('Successfully confirmed your e-mail', 'success')
        app.logger.info('User email confirmed.')
        return redirect(url_for('users'))
    return redirect(url_for('users'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    """
    User registering function
    """
    if request.method == 'POST':
        new_user_username = request.form['username'].lower()
        new_user_email = request.form['email'].lower()
        new_user_password = generate_password_hash(request.form['password'])
        new_user_firstname = request.form['firstname'].capitalize()
        new_user_lastname = request.form['lastname'].capitalize()
        new_user_city = request.form['city'].capitalize()
        new_user_birthday = datetime.datetime.strptime(request.form['birthdate'], '%Y-%m-%d')
        print(new_user_birthday)
        new_user_gender = request.form['gender']
        new_user_registation_date = datetime.datetime.utcnow()
        if request.files['userpic']:
            new_user_userpic = photos.save(request.files['userpic'], name=secrets.token_hex(10) + '.')
        else:
            new_user_userpic = 'default.jpg'

        new_user = User(username=new_user_username,     
                        email=new_user_email,
                        password=new_user_password,
                        firstname=new_user_firstname,
                        lastname=new_user_lastname,
                        city=new_user_city,
                        birthdate=new_user_birthday,
                        gender=new_user_gender,
                        registration_date=new_user_registation_date,
                        userpic=new_user_userpic)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)

        send_confirmation_email(new_user_email)

        flash('Welcome, {}! You\'re registered now. Please, confirm your email'.format(new_user.username), 'success')
        app.logger.info('User created.')
        return redirect(url_for('users'))
    return render_template('register.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    """
    User login function
    """
    if request.method == 'POST':
        username = request.form['username'].lower()
        user_password = request.form['password']
        if '@' in username:
            user_to_login = User.query.filter_by(email=username).first()
        else: 
            user_to_login = User.query.filter_by(username=username).first()
        if user_to_login is None:
            flash('User {} does not exist! Try again.'.format(username), 'danger')
            app.logger.warning('Unsuccessful login attempt.')
            return redirect(url_for('login'))
        else:
            if check_password_hash(user_to_login.password, user_password):
                login_user(user_to_login)
                flash('Welcome, {}! You\'re logged in now.'.format(user_to_login.username), 'success')
                app.logger.info('{} logged in'.format(user_to_login.username))
                return(redirect(url_for('users')))
            else:
                flash('Incorrect password. Try again.', 'danger')
                app.logger.warning('Unsuccessful attempt to log in (wrong password)')
                return(redirect(url_for('login')))
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """
    User logout function
    """
    user_to_logout = current_user
    # person.is_online = False
    logout_user()
    db.session.commit()
    flash('Successfully logged out', 'info')
    app.logger.info('User logged out.')
    return redirect(url_for('login'))


@app.route('/users', methods=['POST', 'GET'])
@login_required
def users():
    all_users = User.all_users()

    user_ids = [user.id for user in all_users]   # list of all user IDs
    # a dictionary {user_id: [list of followers of user_id]}
    flwrs_dict = {usr: all_followers_of_user(usr) for usr in user_ids}
    print(flwrs_dict)

    return render_template('all_users.html', current_user=current_user,
                           all_users=all_users,
                           flwrs_dict=flwrs_dict, all_followers_of_user = all_followers_of_user,
                           all_posts_by_author = Post.all_posts_by_author)


def all_followers_of_user(id):
    # all_followers = User.query.join(followers, (User.id == followers.c.follower_id)).filter_by(user_id=id).all()
    all_followers = User.all_followers(id)
    # all_followers = db.session.query(followers.c.follower_id).filter(followers.c.user_id == id).all()
    # print('ALL FOLLOWERS:', all_followers)

    # return [i._asdict() for i in all_followers]
    return all_followers


@app.route('/users/<username>/profile')
@login_required
def profile(username):
    user_profile = User.get_user_by_username(username)
    
    all_users = User.all_users()

    user_ids = [user.id for user in all_users]
    flwrs_dict = {usr: all_followers_of_user(usr) for usr in user_ids}
    return render_template('profile.html', user_profile=user_profile, 
                                            follow_user=follow_user, 
                                            flwrs_dict=flwrs_dict,
                                            all_followers_of_user=all_followers_of_user,
                                            all_posts_by_author = Post.all_posts_by_author,
                                            all_followed_by_user=User.all_followed_by_user)


@app.route('/users/<username>/profile/edit', methods=['GET', 'POST'])
@login_required
def profile_edit(username):
    if username != current_user.username:
        abort(403)

    user_to_edit = User.get_user_by_username(username)
    if not current_user.id == user_to_edit.id:
        flash('This page is restricted! You cannot edit other users pages', 'danger')
        app.logger.warning('Restricted page access attempt.')
        return redirect(url_for('users'))

    (print(user_to_edit))
    if request.method == 'POST':
        confirm_password = request.form['password']
        if check_password_hash(user_to_edit.password, confirm_password):
            user_to_edit.username = request.form['username']
            user_to_edit.firstname = request.form['firstname']
            user_to_edit.lastname = request.form['lastname']
            user_to_edit.birthdate = request.form['birthdate']
            user_to_edit.city = request.form['city']
            if request.files['userpic']:
                os.remove(basedir + "/static/images/userpics/" + user_to_edit.userpic)
                user_to_edit.userpic = photos.save(request.files['userpic'], name=secrets.token_hex(10) + ".")
            db.session.commit()
            flash('{}\' profile has been successfully updated'.format(user_to_edit.username), 'success')
            app.logger.info('User updated.')
            return redirect(url_for('profile_edit', username=user_to_edit.username))
        else:
            flash('Incorrect password.', 'danger')
            app.logger.info('Incorrect password input.')
            return redirect(url_for('profile_edit', username=user_to_edit.username))


    return render_template('profile_edit.html', user_to_edit=user_to_edit, send_confirmation_email=send_confirmation_email)


@app.route('/users/follow/<username>', methods=['GET', 'POST'])
@login_required
def follow_user(username):
    """
    Folow user function
    """
    user_to_follow = User.query.filter_by(username=username).first() # Select the user to follow
    print(user_to_follow.email)

    # list of users ids who already follows selected user
    users_ids_who_follow_user = db.session.query(followers.c.follower_id).filter(followers.c.user_id == user_to_follow.id).all()
    print(users_ids_who_follow_user)

    # list of users ids who already follows selected user in a LIST format
    users_ids_who_follow_user_list = [follower[0] for follower in users_ids_who_follow_user]
    print(users_ids_who_follow_user_list)

    if current_user.id in users_ids_who_follow_user_list:
        #unfollow
        followers_table_id = db.session.query(followers.c.id).filter(followers.c.user_id == user_to_follow.id, followers.c.follower_id == current_user.id).first()
        print(followers_table_id._asdict()['id'])
        unfollow_user = followers.delete().where(followers.c.id == followers_table_id._asdict()['id'])
        db.session.execute(unfollow_user)
        flash('Now you\'re not following {} anymore :('.format(user_to_follow.username), 'danger')
        app.logger.info('Unfollowed user.')
    else:
        #follow
        follow_usr = followers.insert().values(user_id=user_to_follow.id, follower_id=current_user.id)
        db.session.execute(follow_usr)
        flash('You are now following {}!'.format(user_to_follow.username), 'success')
        app.logger.info('Followed user.')
    db.session.commit()

    return redirect(request.referrer)