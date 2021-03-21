from blog import mail

from flask_mail import Message
from flask import url_for


def send_confirmation_email(email, token):

    msg = Message('Please, confirm your FlaskBlog account',
                    sender='evgenystestmail@yandex.ru',
                    recipients=[email])
    link = url_for('confirm_email',
                   token=token,
                   _external=True)
    msg.body = '''This is FlaskBlog. Please, confirm your e-mail.
                Don\'t reply on this message. 
                This is not spam!\nYour confirmation link: {}'''.format(link)
    mail.send(msg)
    return '<h3>The mail you entered is {}. The token is {}</h3>'\
        .format(email, token)