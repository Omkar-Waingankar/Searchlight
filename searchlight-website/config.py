import os
from flask_mail import Mail, Message

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'n320dNK3j2kfnWKn98dsnlJ8lWe34CV089Wm'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'info.searchlight.ltd@gmail.com' # os.environ["MAIL_USER"]
    MAIL_PASSWORD = 'libtexdat127!' #os.environ["MAIL_PASS"]
