from blog import app, db

from blog.users.models import User
from flask import redirect, render_template, request, flash, url_for, abort
from flask_login import login_user, login_required, logout_user, current_user



@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not current_user.username == 'admin':
        abort(403)

    all_users = User.all_users()
    return render_template('admin/admin.html', all_users=all_users)
