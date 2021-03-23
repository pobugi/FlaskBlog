import datetime
import secrets
from .models import User, followers

from blog import email_sender

from blog import app, db, photos, basedir, mail
from blog.token import generate_confirmation_token, confirm_token
from flask import redirect, render_template, request, flash, url_for
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from blog.config import Config

from itsdangerous import URLSafeTimedSerializer, SignatureExpired

s = URLSafeTimedSerializer(Config.SECRET_KEY)


# @app.route('/')
# def index():
#     if current_user.is_authenticated:
#         return redirect(url_for('users'))
#     return redirect(url_for('login'))

@app.route('/send_confirmation_email/<email_address>')
@login_required
def send_confirmation_email(email_address):
    token = generate_confirmation_token(email_address)
    email_sender.send_confirmation_email(email=email_address, token=token)
    flash('Please check your email and follow the link', 'success')
    return redirect(request.referrer)

@app.route('/confirm_email/<token>')
@login_required
def confirm_email(token):
    """E-mail confirmation"""
    try:
        email = confirm_token(token)
    except SignatureExpired:
        return '<h1>TOKEN EXPIRED</h1>'
    user_to_confirm = User.query.filter_by(email=email).first_or_404()
    if user_to_confirm.is_confirmed:
        return 'This user already confirmed'
    else:
        user_to_confirm.is_confirmed = True
        db.session.add(user_to_confirm)
        db.session.commit()
        flash('Successfully confirmed your e-mail', 'success')
        return redirect(url_for('users'))
    return redirect(url_for('users'))



@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        new_user_username = request.form['username']
        new_user_email = request.form['email']
        new_user_password = generate_password_hash(request.form['password'])
        new_user_firstname = request.form['firstname']
        new_user_lastname = request.form['lastname']
        new_user_city = request.form['city']
        # new_user_birthday = request.form['birthday']
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
                        # birthday=new_user_birthday,
                        gender=new_user_gender,
                        registration_date=new_user_registation_date,
                        userpic=new_user_userpic)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)

        send_confirmation_email(new_user_email)
        # token = generate_confirmation_token(new_user_email)
        # email_sender.send_confirmation_email(email=new_user_email, token=token)

        flash('Welcome, {}! You\'re registered now. Please, confirm your email (we\'ve just sent you a link)'.format(new_user.username), 'success')
        return redirect(url_for('users'))
    return render_template('register.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        user_password = request.form['password']
        if '@' in username:
            user_to_login = User.query.filter_by(email=username).first()
        else: 
            user_to_login = User.query.filter_by(username=username).first()
        if user_to_login is None:
            flash('User {} does not exist! Try again.'.format(username), 'danger')
            return redirect(url_for('login'))
        else:
            if check_password_hash(user_to_login.password, user_password):
                login_user(user_to_login)
                flash('Welcome, {}! You\'re logged in now.'.format(user_to_login.username), 'success')
                return(redirect(url_for('users')))
            else:
                flash('Incorrect password. Try again.', 'danger')
                return(redirect(url_for('login')))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """logs out a user"""
    user_to_logout = current_user
    # person.is_online = False
    logout_user()
    db.session.commit()
    flash('Successfully logged out', 'info')
    return redirect(url_for('login'))


@app.route('/users', methods=['POST', 'GET'])
def users():
    # yyy = db.session.query(User.id).all()

    all_users = User.query.all()

    user_ids = [user.id for user in all_users]   # list of all user IDs
    # a dictionary {user_id: [list of followers of user_id]}
    flwrs_dict = {usr: all_followers_of_user(usr) for usr in user_ids}
    # flwrs_dict = {}
    # for id in user_ids:
    #     flwrs_dict[id] = all_followers_of_user(id)
    print(flwrs_dict)

    return render_template('users.html',    current_user=current_user, 
                                            all_users=all_users, 
                                            flwrs_dict=flwrs_dict, all_followers_of_user = all_followers_of_user)

def all_followers_of_user(id):
    all_followers = User.query.join(followers, (User.id == followers.c.follower_id)).filter_by(user_id=id).all()

    # all_followers = db.session.query(followers.c.follower_id).filter(followers.c.user_id == id).all()
    # print('ALL FOLLOWERS:', all_followers)

    # return [i._asdict() for i in all_followers]
    return all_followers


# @app.route('/users/<int:id>/profile', methods=['GET', 'POST'])
@app.route('/users/<username>/profile', methods=['GET', 'POST'])
@login_required
def profile_edit(username):
    user_to_edit = User.query.filter_by(username=username).first()
    if not current_user.id == user_to_edit.id:
        flash('This page is restricted! You cannot edit other users pages', 'danger')
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
            db.session.commit()
            flash('{}\' profile has been successfully updated'.format(user_to_edit.username), 'success')
            return redirect(url_for('profile_edit', username=user_to_edit.username))
        else:
            flash('Incorrect password.', 'danger')
            return redirect(url_for('profile_edit', id=id))


    return render_template('profile_edit.html', user_to_edit=user_to_edit, send_confirmation_email=send_confirmation_email)




@app.route('/')
def index():

    return 'HELLO'

@app.route('/users/follow/<username>', methods=['GET', 'POST'])
@login_required
def follow_user(username):

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
    else:
        #follow
        follow_usr = followers.insert().values(user_id=user_to_follow.id, follower_id=current_user.id)
        db.session.execute(follow_usr)
        flash('You are now following {}!'.format(user_to_follow.username), 'success')
    db.session.commit()


    # return redirect(url_for('user', username=user_to_follow.username))
    return redirect(request.referrer)





