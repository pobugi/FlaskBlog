import os
import unittest
from string import ascii_lowercase
from random import choice
# from blog import app, db
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from blog.config import Config
from blog.users.models import User

app = Flask(__name__)
db = SQLAlchemy(app)
# db = SQLAlchemy(app)


def rnd_test_db_name():
    """random test database name"""
    name = ''
    for i in range(5):
        name += choice(ascii_lowercase)
    return name + '.db'

def rnd_dummy_data():
    """random username/email"""
    name = ''
    for i in range(5):
        name += choice(ascii_lowercase)
    return name

test_db_name = rnd_test_db_name()

class BasicTestCase(unittest.TestCase):


    def setUp(self):
        """mainpage is html/accessible"""
        app.config.from_object(Config)
        basedir = os.path.abspath(os.path.dirname(__file__))
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(test_db_name)
        self.app = app.test_client()
        db.create_all()

    def test_add_users(self):
        """ensure that user is successfully created"""

        length_before = len(User.query.all()) 

        user1 = User(username=rnd_dummy_data(), email=rnd_dummy_data(), password='password')
        user2 = User(username=rnd_dummy_data(), email=rnd_dummy_data(), password='password')
        user3 = User(username=rnd_dummy_data(), email=rnd_dummy_data(), password='password')

        db.session.add(user1)
        db.session.add(user2)
        db.session.add(user3)

        db.session.commit()
        length_after =len(User.query.all())
        self.assertEqual(length_after, length_before + 3)


    def test_delete_user(self):
        """ensure that user is successfully deleted"""

        user1 = User(username=rnd_dummy_data(), email=rnd_dummy_data(), password='password')
        user2 = User(username=rnd_dummy_data(), email=rnd_dummy_data(), password='password')
        user3 = User(username=rnd_dummy_data(), email=rnd_dummy_data(), password='password')

        db.session.add(user1)
        db.session.add(user2)
        db.session.add(user3)

        db.session.commit()

        length_before = len(User.query.all())

        del_user = User.query.all()[0]
        db.session.delete(del_user)
        db.session.commit()
        length_after = len(User.query.all())
        self.assertEqual(length_after, length_before -1)


    def test_main_page(self):
        """ensure that mainpage type is html/txt and it is accessible"""
        response = self.app.get('/', content_type='html/txt')
        self.assertEqual(response.status_code, 302)

    def test_database_exists(self):
        """ensure that the test database is created successfully"""
        result = os.path.isfile("./blog/{}".format(test_db_name))
        self.assertTrue(result)

    def tearDown(self):
        pass
        # db.session.remove()
        # db.drop_all()
        # os.remove("./blog/{}".format(test_db_name))


if __name__ == "__main__":
    unittest.main()