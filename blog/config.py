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
basedir = os.path.abspath(os.path.dirname(__file__)) #check

class Config(object):

    """Describes basic parameters of the application"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secretkey'
    SECURITY_PASSWORD_SALT = 'email-confirm'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SEND_FILE_MAX_AGE_DEFAULT = 0
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'flaskblogdummy@gmail.com'
    MAIL_PASSWORD = 'Qw987654'
    ADMINS = ['flaskblogdummy@gmail.com']
    TESTING = False
    LOGFILE = 'logs.log'

    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    DEBUG = True
    UPLOADED_PHOTOS_DEST = os.path.join(basedir, 'static/images/userpics')
