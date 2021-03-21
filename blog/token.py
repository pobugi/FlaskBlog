"""
This module is intended to generate and confirm tokens
"""

from itsdangerous import URLSafeTimedSerializer
from blog.config import Config


def generate_confirmation_token(email):

    """Generates e-mail confirmation token"""

    serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
    return serializer.dumps(email, salt=Config.SECURITY_PASSWORD_SALT)


def confirm_token(token, max_age=600):

    """Confirms token"""

    serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
    try:
        email = serializer.loads(token,
                                 salt=Config.SECURITY_PASSWORD_SALT,
                                 max_age=600)
    except:
        return False
    return email