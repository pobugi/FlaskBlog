"""Describes basic parameters of the application"""

import os
# import json

# params_file = open('config.json', 'r')
# params_file_read = params_file.read()
# params = json.loads(params_file_read)
# print(params)
# res = []
# for key in params:
#     res.append(str(key + ' = '+ params[key])+'\n')
# s = ''.join(str(i) for i in res)
# print(s)


class Config(object):

    """Describes basic parameters of the application"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secretkey'
    SECURITY_PASSWORD_SALT = 'email-confirm'
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///database/users.db'
    # SQLALCHEMY_DATABASE_URI = 
    # 'postgresql://postgres:postgres@localhost:5432/users'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SEND_FILE_MAX_AGE_DEFAULT = 0
    # MAIL_SERVER = 'smtp.yandex.ru'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'flaskblogdummy@gmail.com'
    MAIL_PASSWORD = 'Qw987654'
    ADMINS = ['flaskblogdummy@gmail.com']
    # ADMINS = ['evgenystestmail@yandex.ru']
    TESTING = False


    # MAIL_USERNAME = 'twttrspprt@yandex.ru'
    # MAIL_PASSWORD = 'Qw987654'
    #
    # MAIL_USERNAME = 'evgenystestmail@yandex.ru'
    # MAIL_PASSWORD = 'Qw987654'


    # MAIL_USERNAME = 'twttrspprt12@gmail.com'
    # MAIL_PASSWORD = 'Qw987654'
    